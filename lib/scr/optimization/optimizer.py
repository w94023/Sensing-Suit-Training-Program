from ..csv import *
from .common import *
from .callback import *
from .model import *
import copy

from ..pyqt.widget import (CustomMessageBox, AnimatedAxis)

class OptimizationThread(BackgroundThreadWorker):
    pre_training_epoch_end = pyqtSignal(float)
    full_training_epoch_end = pyqtSignal(float)
    embedded_vector_updated = pyqtSignal(list)
    # 작업 완료 시그널
    # bool: data load 성공 여부
    # list: input locations
    # list: output locations
    # int: pre training epoch
    # float: pre training learning rate
    # int: full training epoch
    # float: full training learning rate
    # float: execution time
    # list: embedded vector hist
    # Exception: 오류
    finished = pyqtSignal(bool, list, list, int, float, int, float, list, float, list, Exception)
                                   
    def __init__(self, 
                 file_directory, 
                 dataset,
                 pre_training_epoch,
                 pre_training_learning_rate,
                 full_training_epoch,
                 full_training_learning_rate,
                 lambda1,
                 lambda2,
                 lambda3,
                 parent=None):
        super().__init__(parent)

        # 인스턴스 데이터 저장
        self.file_directory = file_directory
        self.dataset = dataset
        self.pre_training_epoch = pre_training_epoch
        self.pre_training_learning_rate = pre_training_learning_rate
        self.full_training_epoch = full_training_epoch
        self.full_training_learning_rate = full_training_learning_rate
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.lambda3 = lambda3
        self.parent = parent

    def __set_gpu_memory_growth(self):
        # tensorflow가 gpu 메모리 할당 시, 필요한 메모리 점진적으로 증가하도록 설정
        # gpu 메모리 부족으로 인한 오류 시 사용
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
            except RuntimeError as e:
                CustomMessageBox.critical(self.parent, "Optimization error", "Failed to configure GPU memory.")
                
    def __set_gpu_memory_strict(self, memory_size):
        # tensorflow가 gpu 메모리 할당 시, 제한된 메모리만 사용하도록 설정
        # memory_size : MB 단위, 4GB 제한 시 4096 입력 필요
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            try:
                tf.config.set_logical_device_configuration(
                    gpus[0],
                    [tf.config.LogicalDeviceConfiguration(memory_limit=memory_size)])
            except RuntimeError as e:
                CustomMessageBox.critical(self.parent, "Optimization error", "Failed to configure GPU memory.")
             
    def __strain_cutoff(self, header, cutoff):
        input_dataset = pd.DataFrame()
        for data in self.dataset[header+"_input"].values():
            input_dataset = pd.concat([input_dataset, data], axis=0, ignore_index=True)
            
        # Strain difference 계산
        max_strain_values = input_dataset.max()
        min_strain_values = input_dataset.min()
        strain_diff = (max_strain_values-min_strain_values) * 100
        
        # strain_diff가 cutoff 이상인 컬럼 인덱스 반환
        columns_above_cutoff = strain_diff[strain_diff > cutoff].index.tolist()
        return columns_above_cutoff[1:] # Time (s) 열은 버림
           
    def __normalize_dataframe(self, df):
        min_val = df.min().min()  # DataFrame의 최소값
        max_val = df.max().max()  # DataFrame의 최대값

        # 정규화 공식 적용
        normalized_df = (df - min_val) / (max_val - min_val)
        return normalized_df

    def __get_dataset(self, header, input_locations, output_locations):
        input_dataset = pd.DataFrame()
        for data in self.dataset[header+"_input"].values():
            extracted_data = data[input_locations]
            input_dataset = pd.concat([input_dataset, extracted_data], axis=0, ignore_index=True)
            
        output_dataset = pd.DataFrame()
        for data in self.dataset[header+"_output"].values():
            extracted_data = data[output_locations]
            output_dataset = pd.concat([output_dataset, extracted_data], axis=0, ignore_index=True)
            
        # output_dataset = self.__normalize_dataframe(output_dataset)
            
        return input_dataset.to_numpy(), output_dataset.to_numpy()
    
    def set_pre_training_loss(self, loss):
        self.pre_training_epoch_end.emit(loss)
        
    def set_full_training_loss(self, loss):
        self.full_training_epoch_end.emit(loss)
        
    def set_embedded_vector(self, embedded_vector):
        self.embedded_vector_updated.emit(embedded_vector)
    
    def run(self):
        # training input dataset이 설정되지 않았을 경우 예외 처리
        if "training_input" not in self.dataset or len(self.dataset["training_input"]) == 0:
            self.finished.emit(False, [], [], 0, 0.0, 0, 0.0, [], 0.0, [], Exception("No training input data selected."))
            return
        
        # training output dataset이 설정되지 않았을 경우 예외 처리
        if "training_output" not in self.dataset or len(self.dataset["training_output"]) == 0:
            self.finished.emit(False, [], [], 0, 0.0, 0, 0.0, [], 0.0, [], Exception("No training output data selected."))
            return
        
        # # validation input dataset이 설정되지 않았을 경우 예외 처리
        # if "validation_input" not in self.dataset or len(self.dataset["validation_input"]) == 0:
        #     self.finished.emit(False, [], [], 0, 0.0, 0, 0.0, [], 0.0, [], Exception("No validation input data selected."))
        #     return
        
        # # validation output dataset이 설정되지 않았을 경우 예외 처리
        # if "validation_output" not in self.dataset or len(self.dataset["validation_output"]) == 0:
        #     self.finished.emit(False, [], [], 0, 0.0, 0, 0.0, [], 0.0, [], Exception("No validation output data selected."))
        #     return
        
        # data_hist에서, unsaved_data_flag (추가 대기) 및 hide_data_flag (삭제 대기)가 있는 경우에만 저장
        # Output location 설정 (어깨 : 12(구버전) or 14 (신버전), 팔꿈치 : 38, 손목 : 39)
        outputLocation = [12, 38, 39]
        output_locations = []
        for i in outputLocation:
            output_locations.append("Marker"+str(i)+"X")
            output_locations.append("Marker"+str(i)+"Y")
            output_locations.append("Marker"+str(i)+"Z")
            
        input_locations = self.__strain_cutoff("training", 20)
        # input_locations = []
        # for i in range(102):
        #     input_locations.append("Wireframe"+str(i+1))
        
        # dataset으로부터 training, validation 데이터의 input 및 output 데이터 추출
        training_input, training_output = self.__get_dataset("training", input_locations, output_locations)
        # validation_input, validation_output = self.__get_dataset("validation", input_locations, output_locations)
        
        if not self.is_running:
            self.finished.emit(False, [], [], 0, 0.0, 0, 0.0, [], 0.0, [], Exception("The operation was canceled by the user."))
            return
        
        self.update_progress(5) # 데이터 추출 완료
           
        # pre training model 및 full training model 생성 관리하는 빌더 생성
        batch_size = np.shape(training_input)[0]
        model_builder = ModelBuilder(
            input_size = np.shape(training_input)[1], 
            output_size = np.shape(training_output)[1], 
            pre_training_learning_rate = self.pre_training_learning_rate, 
            full_training_learning_rate = self.full_training_learning_rate
        )
            
        # gpu 메모리 사용 기준 설정
        self.__set_gpu_memory_growth()
        
        if not self.is_running:
            self.finished.emit(False, [], [], 0, 0.0, 0, 0.0, [], 0.0, [], Exception("The operation was canceled by the user."))
            return
        
        self.update_progress(10) # 학습 준비 완료
        
        execution_time_start_point = time.time()
        
        print('Pre-training')
        
        # pre training (encoder network의 값을 1에 수렴)
        pre_training_model_callback = PreTrainingCallback(self)
        pre_trained_encoder_model = model_builder.build_encoder_model()
        pre_trained_encoder_model.fit(training_input, np.full(np.shape(training_input), 1), epochs = self.pre_training_epoch, batch_size = batch_size, verbose = 0, callbacks = [pre_training_model_callback])
        encoder_weights = pre_trained_encoder_model.get_weights()
        
        if not self.is_running:
            self.finished.emit(False, [], [], 0, 0.0, 0, 0.0, [], 0.0, [], Exception("The operation was canceled by the user."))
            return
            
        print('Full-training')
        
        # full training (optimal sensor location finding)
        # stage 1
        full_training_model_callback = FullTrainingCallback(self, self.pre_training_epoch, training_input)
        full_training_model_callback.progress_bias = 50
        model = model_builder.build_full_model(encoder_weights, [], True, False, self.lambda1)
        model.fit(training_input, training_output, epochs = self.full_training_epoch, batch_size = batch_size, verbose = 0, callbacks = [full_training_model_callback])
        weights = model.get_weights()
        
        if not self.is_running:
            self.finished.emit(False, [], [], 0, 0.0, 0, 0.0, [], 0.0, [], Exception("The operation was canceled by the user."))
            return
            
        # # stage 2
        # full_training_model_callback.progress_bias = 50
        # model =  model_builder.build_full_model(encoder_weights, weights[6:20], True, True, self.lambda2)
        # model.fit(training_input, training_output, epochs = self.full_training_epoch, batch_size = batch_size, verbose = 0, callbacks = [full_training_model_callback])
        # weights = model.get_weights()
        
        # if not self.is_running:
        #     self.finished.emit(False, [], [], 0, 0.0, 0, 0.0, [], 0.0, [], Exception("The operation was canceled by the user."))
        #     return
            
        # # stage 3
        # full_training_model_callback.progress_bias = 75
        # model =  model_builder.build_full_model(encoder_weights, weights[6:20], True, True, self.lambda3)
        # model.fit(training_input, training_output, epochs = self.full_training_epoch, batch_size = batch_size, verbose = 0, callbacks = [full_training_model_callback])
        # weights = model.get_weights()
        
        # if not self.is_running:
        #     self.finished.emit(False, [], [], 0, 0.0, 0, 0.0, [], 0.0, [], Exception("The operation was canceled by the user."))
        #     return
        
        execution_time_end_point = time.time()
        
        self.update_progress(100) # progress 완료
        
        # # 모델 파일 저장
        # print(os.path.join(self.file_directory, "test_model"))
        # model.save(os.path.join(self.file_directory, "test_model"))
        
        self.finished.emit(True,
                           input_locations,
                           output_locations,
                           self.pre_training_epoch,
                           self.pre_training_learning_rate,
                           self.full_training_epoch,
                           self.full_training_learning_rate,
                           [self.lambda1, self.lambda2, self.lambda3],
                           execution_time_end_point - execution_time_start_point,
                           full_training_model_callback.get_embedded_vector_hist(),
                           Exception())
        
def rmse(y_true, y_pred):
    mse = np.mean((y_true - y_pred) ** 2)  # 평균 제곱 오차(MSE) 계산
    rmse = np.sqrt(mse)  # 평균 제곱근 오차(RMSE) 계산
    return rmse

class Optimizer():
    def __init__(self, file_directory, callbacks, parent=None):
        self.file_directory = file_directory
        self.pre_training_loss_update_callback = callbacks[0]
        self.full_training_loss_update_callback = callbacks[1]
        self.embedded_vector_update_callback = callbacks[2]
        self.parent = parent
        
        self.dataset = {}
        
        # 백그라운드 스레드 생성
        self.optimization_thread = None
        
        # 오래 걸리는 작업을 처리하기 위한 dialog 생성
        self.optimization_dialog = ProgressDialog("Optimization progress", self.parent)
        
    def set_dataset(self, dataset, header, type):
        self.dataset[header+"_"+type] = copy.deepcopy(dataset)
        
    def start_optimization(self, pre_training_epoch, pre_training_learning_rate, full_training_epoch, full_training_learning_rate, lambda1, lambda2, lambda3):

        if self.optimization_thread is not None:
            CustomMessageBox.critical(self.parent, "Optimization error", "The previous optimization task has not been completed.")
            return
        
        # 작업 시작 window 표시
        self.optimization_dialog.start_progress()
        
        # 백그라운드 스레드 생성
        self.optimization_thread = OptimizationThread(self.file_directory,
                                                      self.dataset,
                                                      pre_training_epoch, 
                                                      pre_training_learning_rate, 
                                                      full_training_epoch, 
                                                      full_training_learning_rate, 
                                                      lambda1, 
                                                      lambda2, 
                                                      lambda3, 
                                                      self.parent)
        self.optimization_thread.pre_training_epoch_end.connect(self.__update_pre_training_progress)
        self.optimization_thread.full_training_epoch_end.connect(self.__update_full_training_progress)
        self.optimization_thread.embedded_vector_updated.connect(self.__update_embedded_vector)
        self.optimization_thread.finished.connect(self.__on_optimization_finished)
        self.optimization_dialog.set_worker(self.optimization_thread) # 백그라운드 스레드 설정
        self.optimization_thread.start()
        
    def __update_pre_training_progress(self, training_loss):
        self.pre_training_loss_update_callback(training_loss)
        
    def __update_full_training_progress(self, training_loss):
        self.full_training_loss_update_callback(training_loss)
        
    def __update_embedded_vector(self, embedded_vector):
        self.embedded_vector_update_callback(embedded_vector)
            
    def __get_embedded_vector_df(self, input_locations, embedded_vector_hist):
        columns = []
        for location in input_locations:
            columns.append(str(location))
            
        df = pd.DataFrame(embedded_vector_hist, columns=columns)
        return df
        
    def __on_optimization_finished(self,
                                   result,
                                   input_locations,
                                   output_locations,
                                   pre_training_epoch,
                                   pre_training_learning_rate,
                                   full_training_epoch,
                                   full_training_learning_rate,
                                   lambdas,
                                   execution_time,
                                   embedded_vector_hist,
                                   exception):
        self.optimization_dialog.stop_progress()
        
        if result is True:
            embedded_vector_hist_df = self.__get_embedded_vector_df(input_locations, embedded_vector_hist)
            
            # 마지막 행 추출 (.iloc[0] : series 형태로 가져옴)
            result = embedded_vector_hist_df.tail(1).iloc[0]
            
            selected_wireframes = result[result != 0].index.tolist()  # 값이 0이 아닌 컬럼 헤더 추출
            
            # CSV 파일 저장 경로 선택
            directory_path = QFileDialog.getExistingDirectory(self.parent, "Select Directory", "", QFileDialog.ShowDirsOnly)
    
            # CSV 파일 생성
            with open(os.path.join(directory_path, "Embedded_Vector.csv"), mode='w', newline='') as file:
                writer = csv.writer(file)

                # Pre training 설정 작성
                writer.writerow([" "] + ["Pre training epoch / learning rate"] + [pre_training_epoch] + [pre_training_learning_rate])
                
                # Full training 설정 작성
                writer.writerow([" "] + ["Full training epoch / learning rate"] + [full_training_epoch] + [full_training_learning_rate])
                
                # 빈 행 추가
                writer.writerow([])
                
                # Execution time 작성
                writer.writerow([" "] + ["Execution time"] + [execution_time])
                
                # 빈 행 추가
                writer.writerow([])
                
                # Lambda 값 작성
                writer.writerow([" "] + ["Lambdas"] + lambdas)
                
                # 빈 행 추가
                writer.writerow([])
                
                # Selected wireframe 작성
                writer.writerow([" "] + ["Selected locations"] + selected_wireframes)
                
                # 빈 행 추가
                writer.writerow([])
                
                # Input location, output location 작성
                writer.writerow([" "] + ["Output locations"] + output_locations)
                writer.writerow([" "] + ["Input locations"] + input_locations)
                
                # DataFrame 행 데이터에 첫 열에 공백 추가
                rows_with_blank = [[" "] + [" "] + list(row) for row in embedded_vector_hist_df.values]
    
                # DataFrame의 내용을 작성
                writer.writerows(rows_with_blank)
            
            CustomMessageBox.information(self.parent, "Information", "Data has been optimized successfully.")
        else:
            CustomMessageBox.critical(self.parent, "Error", "Failed to optimize data : " + str(exception))
            
        self.optimization_thread = None
        self.optimization_dialog.set_worker(self.optimization_thread) # dialog 최신화