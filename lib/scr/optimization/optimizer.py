from .common import *
from .callback import *
from .model import *
import copy

class OptimizationThread(BackgroundThreadWorker):
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
    finished = pyqtSignal(bool, list, list, int, float, int, float, float, list, Exception)
                                   
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
                
    def __get_dataset(self, header, input_locations, output_locations):
        input_dataset = pd.DataFrame()
        for data in self.dataset[header+"_input"].values():
            extracted_data = data[input_locations]
            input_dataset = pd.concat([input_dataset, extracted_data], axis=0, ignore_index=True)
            
        output_dataset = pd.DataFrame()
        for data in self.dataset[header+"_output"].values():
            extracted_data = data[output_locations]
            output_dataset = pd.concat([output_dataset, extracted_data], axis=0, ignore_index=True)
            
        return input_dataset.to_numpy(), output_dataset.to_numpy()
    
    def run(self):
        # training input dataset이 설정되지 않았을 경우 예외 처리
        if "training_input" not in self.dataset or len(self.dataset["training_input"]) == 0:
            self.finished.emit(False, [], [], None, None, None, None, None, [], Exception("No training input data selected."))
            return
        
        # training output dataset이 설정되지 않았을 경우 예외 처리
        if "training_output" not in self.dataset or len(self.dataset["training_output"]) == 0:
            self.finished.emit(False, [], [], None, None, None, None, None, [], Exception("No training output data selected."))
            return
        
        # validation input dataset이 설정되지 않았을 경우 예외 처리
        if "validation_input" not in self.dataset or len(self.dataset["validation_input"]) == 0:
            self.finished.emit(False, [], [], None, None, None, None, None, [], Exception("No validation input data selected."))
            return
        
        # validation output dataset이 설정되지 않았을 경우 예외 처리
        if "validation_output" not in self.dataset or len(self.dataset["validation_output"]) == 0:
            self.finished.emit(False, [], [], None, None, None, None, None, [], Exception("No validation output data selected."))
            return
        
        # data_hist에서, unsaved_data_flag (추가 대기) 및 hide_data_flag (삭제 대기)가 있는 경우에만 저장
        outputLocation = [1, 2, 3]
        output_locations = []
        for i in outputLocation:
            output_locations.append("Marker"+str(i)+"X")
            output_locations.append("Marker"+str(i)+"Y")
            output_locations.append("Marker"+str(i)+"Z")
            
        inputLocation = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 29, 31, 32, 33, 38, 44, 45, 48, 49, 51, 53, 55, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102]
        input_locations = []
        for i in inputLocation:
            input_locations.append("Wireframe"+str(i))
            
        # dataset으로부터 training, validation 데이터의 input 및 output 데이터 추출
        training_input,   training_output   = self.__get_dataset("training", input_locations, output_locations)
        validation_input, validation_output = self.__get_dataset("validation", input_locations, output_locations)
        
        if not self.is_running:
            self.finished.emit(False, [], [], None, None, None, None, None, [], Exception("The operation was canceled by the user."))
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
            self.finished.emit(False, [], [], None, None, None, None, None, [], Exception("The operation was canceled by the user."))
            return
        
        self.update_progress(10) # 학습 준비 완료
        
        execution_time_start_point = time.time()
        
        # pre training (encoder network의 값을 1에 수렴)
        pre_training_model_callback = PreTrainingCallback(self, self.pre_training_epoch)
        pre_trained_encoder_model = model_builder.build_encoder_model()
        pre_trained_encoder_model.fit(training_input, np.full(np.shape(training_input), 1), epochs = self.pre_training_epoch, batch_size = batch_size, verbose = 0, callbacks = [pre_training_model_callback])
        encoder_weights = pre_trained_encoder_model.get_weights()
        
        if not self.is_running:
            self.finished.emit(False, [], [], None, None, None, None, None, [], Exception("The operation was canceled by the user."))
            return
            
        # full training (optimal sensor location finding)
        # stage 1
        full_training_model_callback = FullTrainingCallback(self, self.pre_training_epoch, training_input)
        model =  model_builder.build_full_model(encoder_weights, [], True, False, 0.2)
        model.fit(training_input, training_output, epochs = self.full_training_epoch, batch_size = batch_size, verbose = 0, callbacks = [full_training_model_callback])
        weights = model.get_weights()
        
        if not self.is_running:
            self.finished.emit(False, [], [], None, None, None, None, None, [], Exception("The operation was canceled by the user."))
            return
            
        # stage 2
        model =  model_builder.build_full_model(encoder_weights, weights[6:20], True, True, 0.5)
        model.fit(training_input, training_output, epochs = self.full_training_epoch, batch_size = batch_size, verbose = 0, callbacks = [full_training_model_callback])
        weights = model.get_weights()
        
        if not self.is_running:
            self.finished.emit(False, [], [], None, None, None, None, None, [], Exception("The operation was canceled by the user."))
            return
            
        # stage 3
        model =  model_builder.build_full_model(encoder_weights, weights[6:20], True, True, 0.8)
        model.fit(training_input, training_output, epochs = self.full_training_epoch, batch_size = batch_size, verbose = 0, callbacks = [full_training_model_callback])
        weights = model.get_weights()
        
        if not self.is_running:
            self.finished.emit(False, [], [], None, None, None, None, None, [], Exception("The operation was canceled by the user."))
            return
        
        execution_time_end_point = time.time()
        
        self.update_progress(100) # progress 완료
        
        # 모델 파일 저장
        print(os.path.join(self.file_directory, "test_model"))
        model.save(os.path.join(self.file_directory, "test_model"))
        
        self.finished.emit(True,
                           input_locations,
                           output_locations,
                           self.pre_training_epoch,
                           self.pre_training_learning_rate,
                           self.full_training_epoch,
                           self.full_training_learning_rate,
                           execution_time_end_point - execution_time_start_point,
                           full_training_model_callback.get_embedded_vector_hist(),
                           Exception())
        
def rmse(y_true, y_pred):
    mse = np.mean((y_true - y_pred) ** 2)  # 평균 제곱 오차(MSE) 계산
    rmse = np.sqrt(mse)  # 평균 제곱근 오차(RMSE) 계산
    return rmse

class Optimizer():
    def __init__(self, file_directory, parent=None):
        self.file_directory = file_directory
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
        self.optimization_thread.finished.connect(self.__on_optimization_finished)
        self.optimization_dialog.set_worker(self.optimization_thread) # 백그라운드 스레드 설정
        self.optimization_thread.start()
        
            # # Save training results
            # training_result = np.vstack((
            #     np.array(input_locations),
            #     variable_into_padded_array(pre_training_learning_rate, shape = (np.size(input_locations, 0), )),
            #     variable_into_padded_array(full_training_learning_rate, shape = (np.size(input_locations, 0), )),
            #     variable_into_padded_array(interface.execution_time, shape = (np.size(input_locations, 0), )),
            #     full_training_model_callback.get_stacked_arr()
            # ))
            # training_result_label = np.array([
            #     ['Input locations'], 
            #     ['Pre training learning rate'], 
            #     ['Full training learning rate'], 
            #     ['Execution Time (s)'], 
            #     ['Embedded vector values']
            # ])
            # training_result_label = variable_into_padded_array(training_result_label, shape = (np.size(training_result, 0), 1))
            # csvwrite(path+'/Results/'+get_current_time_in_string()+".csv", np.hstack((training_result_label, training_result)))
            
    def __on_optimization_finished(self,
                                   result,
                                   input_locations,
                                   output_locations,
                                   pre_training_epoch,
                                   pre_training_learning_rate,
                                   full_training_epoch,
                                   full_training_learning_rate,
                                   execution_time,
                                   embedded_vector_hist,
                                   exception):
        self.optimization_dialog.stop_progress()
        
        if result is True:
            CustomMessageBox.information(self.parent, "Information", "Data has been optimized successfully.")
            print(input_locations)
            print(output_locations)
            print(pre_training_epoch, pre_training_learning_rate)
            print(full_training_epoch, full_training_learning_rate)
            print(execution_time)
            print(embedded_vector_hist)
        else:
            CustomMessageBox.critical(self.parent, "Error", "Failed to optimize data : " + str(exception))
            
        self.optimization_thread = None
        self.optimization_dialog.set_worker(self.optimization_thread) # dialog 최신화