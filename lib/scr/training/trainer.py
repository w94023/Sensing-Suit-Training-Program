from ..csv import *
from .common import *
# from .callback import *
# from .model import *
import copy
import keras
from keras.initializers import glorot_normal

from ..pyqt.widget import (CustomMessageBox)

class TrainingThread(BackgroundThreadWorker):
    # Epoch 완료 시그널
    # float : training loss
    # float : validation loss
    on_epoch_end = pyqtSignal(float, float)
    # 작업 완료 시그널
    # bool: training 성공 여부
    # list: input locations
    # list: output locations
    # int: epoch
    # float: learning rate
    # int : iteration
    # float: execution time
    # object : best trained model
    # Exception: 오류
    on_progress_finished = pyqtSignal(bool, list, list, int, float, int, float, object, Exception)
                                   
    def __init__(self, 
                 file_directory, 
                 dataset,
                 input_locations,
                 output_locations,
                 training_epoch,
                 training_learning_rate,
                 parent=None):
        super().__init__(parent)

        # 인스턴스 데이터 저장
        self.file_directory = file_directory
        self.dataset = dataset
        self.input_locations = input_locations
        self.output_locations = output_locations
        self.training_epoch = training_epoch
        self.training_learning_rate = training_learning_rate
        self.parent = parent
        
        self.best_model = None
    
    def check_model(self, model, loss, val_loss_hist):
        # training loss : loss[0][0] / validation loss : loss[1][0]
        train_loss = loss[0][0]
        val_loss = loss[1][0]
        
        self.on_epoch_end.emit(train_loss, val_loss)
        
        # Validation loss history 저장
        val_loss_hist.append(val_loss)

        min_val_loss = min(val_loss_hist)
        if val_loss <= min_val_loss:
            self.best_model = model
            
        return val_loss_hist
    
    def run(self):
        # training input dataset이 설정되지 않았을 경우 예외 처리
        if "training_input" not in self.dataset or len(self.dataset["training_input"]) == 0:
            self.on_progress_finished.emit(False, [], [], 0, 0.0, 0, 0.0, None, Exception("No training input data selected."))
            return
        
        # training output dataset이 설정되지 않았을 경우 예외 처리
        if "training_output" not in self.dataset or len(self.dataset["training_output"]) == 0:
            self.on_progress_finished.emit(False, [], [], 0, 0.0, 0, 0.0, None, Exception("No training output data selected."))
            return
        
        # validation input dataset이 설정되지 않았을 경우 예외 처리
        if "validation_input" not in self.dataset or len(self.dataset["validation_input"]) == 0:
            self.on_progress_finished.emit(False, [], [], 0, 0.0, 0, 0.0, None, Exception("No validation input data selected."))
            return
        
        # validation output dataset이 설정되지 않았을 경우 예외 처리
        if "validation_output" not in self.dataset or len(self.dataset["validation_output"]) == 0:
            self.on_progress_finished.emit(False, [], [], 0, 0.0, 0, 0.0, None, Exception("No validation output data selected."))
            return
        
        # Output location 설정 (어깨 : 12(구버전) or 14 (신버전), 팔꿈치 : 38, 손목 : 39)
        output_locations = []
        for location in self.output_locations:
            output_locations.append("Marker"+location+"X")
            output_locations.append("Marker"+location+"Y")
            output_locations.append("Marker"+location+"Z")
            
        # Input location 설정
        input_locations = []
        for location in self.input_locations:
            input_locations.append("Wireframe"+location)
        
        # dataset으로부터 training, validation 데이터의 input 및 output 데이터 추출
        training_input, training_output = get_dataset(self.dataset, "training", input_locations, output_locations)
        validation_input, validation_output = get_dataset(self.dataset, "validation", input_locations, output_locations)
        
        if not self.is_running:
            self.on_progress_finished.emit(False, [], [], 0, 0.0, 0, 0.0, None, Exception("The operation was canceled by the user."))
            return
        
        self.update_progress(5) # 데이터 추출 완료
        
        # gpu 메모리 사용 기준 설정
        set_gpu_memory_growth(self.parent)
        
        execution_time_start_point = time.time()
        
        # 러닝 설정 (GPU 사용)
        batch = np.size(training_input, 0)
        layerSize = 128
        opt = keras.optimizers.Adamax(learning_rate=self.training_learning_rate, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0)
        
        with tf.device('/device:GPU:0'):
            X = Input(shape=(np.size(training_input, 1), ))
            Y = Dense(layerSize,                   activation = 'relu',   kernel_initializer = glorot_normal(seed=1))(X)
            Y = Dense(layerSize,                   activation = 'relu',   kernel_initializer = glorot_normal(seed=1))(Y)
            Y = Dense(layerSize,                   activation = 'relu',   kernel_initializer = glorot_normal(seed=1))(Y)
            Y = Dense(layerSize,                   activation = 'relu',   kernel_initializer = glorot_normal(seed=1))(Y)
            Y = Dense(layerSize,                   activation = 'relu',   kernel_initializer = glorot_normal(seed=1))(Y)
            Y = Dense(layerSize,                   activation = 'relu',   kernel_initializer = glorot_normal(seed=1))(Y)
            Y = Dense(np.size(training_output, 1), activation = 'linear', kernel_initializer = glorot_normal(seed=1))(Y)

            model = Model(inputs = [X], outputs = [Y])
            model.compile(loss='mean_squared_error', optimizer=opt, metrics=['accuracy'])
            
            self.update_progress(10) # 학습 준비 완료

            # Validation loss 이력 초기화
            val_loss_hist = []

            # 러닝 시작
            learning_iteration = 1
            while self.is_running:
                
                hist = model.fit(training_input, training_output, validation_data = (validation_input, validation_output), epochs=1, batch_size=batch, verbose = 0)
                loss = [hist.history['loss'], hist.history['val_loss']]

                # 인터페이스 출력
                val_loss_hist = self.check_model(model, loss, val_loss_hist)
                
                self.update_progress(learning_iteration/self.training_epoch * 90 + 10)

                # Preset epoch 도달 시 종료
                if learning_iteration == self.training_epoch:
                    break

                learning_iteration += 1

        # # 가장 학습이 잘된 모델 따로 저장
        # filename = str(min(val_loss_hist)) + ".h5"
        # print(filename)
        # if self.best_model is not None:
        #     self.best_model.save(os.path.join(self.file_directory, filename))
 
        execution_time_end_point = time.time()
        
        self.update_progress(100) # progress 완료
        
        self.on_progress_finished.emit(True,
                                       input_locations,
                                       output_locations,
                                       self.training_epoch,
                                       self.training_learning_rate,
                                       learning_iteration,
                                       execution_time_end_point - execution_time_start_point,
                                       self.best_model,
                                       Exception())
        
# def rmse(y_true, y_pred):
#     mse = np.mean((y_true - y_pred) ** 2)  # 평균 제곱 오차(MSE) 계산
#     rmse = np.sqrt(mse)  # 평균 제곱근 오차(RMSE) 계산
#     return rmse

class Trainer():
    def __init__(self, file_directory, callbacks, parent=None):
        self.file_directory = file_directory
        self.trainig_loss_update_callback = callbacks[0]
        self.validation_loss_update_callback = callbacks[1]
        self.test_result_update_callback = callbacks[2]
        self.test_result_export_callback = callbacks[3]
        self.parent = parent
        
        self.dataset = {}
        
        # 백그라운드 스레드 생성
        self.training_thread = None
        
        # 오래 걸리는 작업을 처리하기 위한 dialog 생성
        self.training_progress_dialog = ProgressDialog("Training progress", self.parent)
        
    def set_dataset(self, dataset, header, type):
        self.dataset[header+"_"+type] = copy.deepcopy(dataset)
        
    def start_training(self, input_locations, output_locations, training_epoch, training_learning_rate):
        if self.training_thread is not None:
            CustomMessageBox.critical(self.parent, "Training error", "The previous training task has not been completed.")
            return
        
        # 작업 시작 window 표시
        self.training_progress_dialog.start_progress()
        
        # 백그라운드 스레드 생성
        self.training_thread = TrainingThread(self.file_directory,
                                              self.dataset,
                                              input_locations,
                                              output_locations,
                                              training_epoch, 
                                              training_learning_rate, 
                                              self.parent)
        self.training_thread.on_epoch_end.connect(self.__update_loss)
        self.training_thread.on_progress_finished.connect(self.__on_training_finished)
        self.training_progress_dialog.set_worker(self.training_thread) # 백그라운드 스레드 설정
        self.training_thread.start()
        
    def __update_loss(self, training_loss, validation_loss):
        self.trainig_loss_update_callback(training_loss)
        self.validation_loss_update_callback(validation_loss)
        
    def __get_rmse(self, reference_data, estimated_data):
        return np.sqrt(np.mean((reference_data - estimated_data) ** 2))
        
    def __on_training_finished(self,
                               result,
                               input_locations,
                               output_locations,
                               training_epoch,
                               training_learning_rate,
                               learning_iteration,
                               execution_time,
                               best_model,
                               exception):
        self.training_progress_dialog.stop_progress()
        
        if result is True:
            # Test dataset 추출
            test_input, test_output, time_label = get_dataset(self.dataset, "test", input_locations, output_locations, get_time_label=True)
            test_estimated = best_model.predict(test_input, verbose=0)
            rmse = self.__get_rmse(test_output, test_estimated)
            
            self.test_result_update_callback(time_label, test_estimated, test_output, rmse)
            self.test_result_export_callback(training_epoch, training_learning_rate, learning_iteration, execution_time, input_locations, output_locations, rmse, test_estimated, test_output, time_label)
            
            CustomMessageBox.information(self.parent, "Information", "Network has been trained successfully.")
        else:
            CustomMessageBox.critical(self.parent, "Error", "Failed to train network : " + str(exception))
            
        self.training_thread = None
        self.training_progress_dialog.set_worker(self.training_thread) # dialog 최신화