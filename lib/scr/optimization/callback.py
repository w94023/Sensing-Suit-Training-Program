from .common import *

class FullTrainingCallback(tf.keras.callbacks.Callback):
    def __init__(self, optimizer, total_epoch, training_input):
        super(FullTrainingCallback, self).__init__()
        
        self.optimizer = optimizer
        self.total_epoch = total_epoch
        # embedded vector output 도출을 위한 training input 저장
        self.training_input = training_input
        # embedded vector과 연결된 layer 저장
        self.intermediate_layer_model = None
        self.embedded_vector_hist = []
        self.progress_bias = 0
        
    def on_epoch_begin(self, epoch, logs = None):
        # 첫 번째 iteration에서 embedded vector과 연결된 layer 인스턴스 변수에 저장
        if epoch == 0:
            self.intermediate_layer_model = tf.keras.Model(inputs = self.model.inputs, outputs = self.model.get_layer('embeddedVector').output)
        
    def on_epoch_end(self, epoch, logs = None):
        training_loss = logs['loss']
        intermediate_output = self.intermediate_layer_model.predict_on_batch(self.training_input)
        intermediate_output_mean = np.mean(intermediate_output, axis = 0)
        self.embedded_vector_hist.append(intermediate_output_mean)
        
        # training_loss 전달
        self.optimizer.set_full_training_loss(training_loss)
        
        # Embedded vector 전달
        self.optimizer.set_embedded_vector(intermediate_output_mean.tolist())
        
        # Progress bar 업데이트
        self.optimizer.update_progress(self.progress_bias + (epoch+1)/self.optimizer.full_training_epoch * 50)
        
        # Stop 요청 시 중지
        if not self.optimizer.is_running:
            self.model.stop_training = True
            
    def get_embedded_vector_hist(self):
        return self.embedded_vector_hist
    
class PreTrainingCallback(tf.keras.callbacks.Callback):
    def __init__(self, optimizer):
        super(PreTrainingCallback, self).__init__()
        
        self.optimizer = optimizer
        self.y_data = []
        
    def on_epoch_end(self, epoch, logs = None):
        training_loss = logs['loss']
        
        # training_loss 전달
        self.optimizer.set_pre_training_loss(training_loss)
        
        # Progress bar 업데이트
        self.optimizer.update_progress(10 + (epoch+1)/self.optimizer.pre_training_epoch * 40)
        
        # Stop 요청 시 중지
        if not self.optimizer.is_running:
            self.model.stop_training = True