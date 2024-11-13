from .common import *
import copy

def rmse(y_true, y_pred):
    mse = np.mean((y_true - y_pred) ** 2)  # 평균 제곱 오차(MSE) 계산
    rmse = np.sqrt(mse)  # 평균 제곱근 오차(RMSE) 계산
    return rmse
    
# class CustomCallback(tf.keras.callbacks.Callback):
#     def __init__(self, testInput, interface = None):
#         super(CustomCallback, self).__init__()
#         self.interface = interface
#         self.interface.is_full_model_training = True
        
#         self.intermediate_layer_model = None
#         self.testInput = testInput
#         self.stacked_arr = []
        
#     def on_epoch_begin(self, epoch, logs = None):
#         if epoch == 0:
#             self.intermediate_layer_model = tf.keras.Model(inputs = self.model.inputs, outputs = self.model.get_layer('embeddedVector').output)
        
#     def on_epoch_end(self, epoch, logs = None):
#         trainLoss = logs['loss']
#         intermediate_output = self.intermediate_layer_model.predict_on_batch(self.testInput)
#         self.intermediate_output_mean = np.mean(intermediate_output, axis = 0)
#         self.msg = ""
#         for i in range(np.size(self.intermediate_output_mean, 0)):
#             self.msg += format(self.intermediate_output_mean[i], '.2f') + " "
        
#         self.stacked_arr.append(self.intermediate_output_mean)
        
#         if self.interface != None:
#             self.interface.update_full_model_interface(epoch+1, trainLoss, 0, 0, self.msg)
#             if not self.interface.is_full_model_training:
#                 self.model.stop_training = True
    
#     def get_stacked_arr(self):
#         return np.vstack(self.stacked_arr)
    
# class CustomCallback2(tf.keras.callbacks.Callback):
#     def __init__(self, interface = None):
#         super(CustomCallback2, self).__init__()
#         self.interface = interface
        
#     def on_epoch_end(self, epoch, logs = None):
#         trainLoss = logs['loss']
#         if self.interface != None:
#             # self.interface.update(epoch+1, trainLoss, 0, 0)
#             self.interface.update_encoder_model_interface(epoch+1, trainLoss)
#             if not self.interface.is_encoder_model_training:
#                 self.model.stop_training = True
                
# class CustomCallback3(tf.keras.callbacks.Callback):
#     def __init__(self, interface = None):
#         super(CustomCallback3, self).__init__()
#         self.interface = interface
#         self.bestValLoss = math.inf
#         self.bestModel = None
        
#     def on_epoch_end(self, epoch, logs = None):
            
#         trainLoss = logs['loss']
#         valLoss   = logs['val_loss']
#         if valLoss < self.bestValLoss:
#             self.bestValLoss = valLoss
#             self.bestModel = self.model
        
#         if self.interface != None:
#             self.interface.update_decoder_model_interface(epoch+1, trainLoss, valLoss, self.bestValLoss)
#             if not self.interface.is_decoder_model_training:
#                 self.model.stop_training = True
                
#     def getBestModel(self):
#         return self.bestModel

# def save_weights_and_biases(path, model):
#     weights = model.get_weights()
#     for i in range(int(len(weights) / 2)):
#         csvwrite((path+'Weight'+str(i)+'.csv'), weights[2*i])
#         csvwrite((path+'Bias'+str(i)+'.csv'), weights[2*i+1])
        
# def load_weigths_and_biases(path):
#     # Check file in path
#     # [Bias0.csv, ..., BiasN.csv, Weight0.csv, ..., WeightN.csv]
#     file_list = os.listdir(path)
#     file_count = len(file_list)
    
#     weights = []
#     for i in range(file_count // 2):
#         weights.append(csvread(path+file_list[i + file_count // 2], 0, 0)) # Weights
#         weights.append(csvread(path+file_list[i], 0, 0)) # Biases
        
#     return weights

import tensorflow as tf
# from tensorflow import keras
from keras import optimizers
from keras.layers import Input, Dense, Multiply, Layer
from keras.models import Model
import keras.backend as K

def custom_sigmoid(x):
    condition = K.greater_equal(x, 0.0)
    return K.switch(condition, K.tanh(x), tf.zeros_like(x))

def custom_loss(model, alpha):
    def loss(y_true, y_pred):
        # Mean squared error
        mse = K.mean(K.square(y_pred - y_true), axis=-1)
        # 최종 손실 계산
        return mse * alpha
    return loss

class ModelBuilder():
    def __init__(self, input_size, output_size, pre_training_learning_rate, full_training_learning_rate):
        self.input_size = input_size
        self.output_size = output_size
        self.pre_training_optimizer = optimizers.Adam(learning_rate = pre_training_learning_rate, beta_1 = 0.9, beta_2 = 0.999, epsilon = None, decay = 0)
        self.full_training_optimizer = optimizers.Adam(learning_rate = full_training_learning_rate, beta_1 = 0.9, beta_2 = 0.999, epsilon = None, decay = 0)

    def build_encoder_model(self):
        X = Input(shape = (self.input_size, ))
        Y = Dense(128, activation = 'relu')(X)
        Y = Dense(64, activation = 'relu')(Y)
        Y = Dense(self.input_size, activation = 'linear')(Y)
        pre_trained_model = Model(inputs = [X], outputs = [Y])
        pre_trained_model.compile(loss = 'mean_squared_error', optimizer = self.pre_training_optimizer, metrics = ['accuracy'])
        return pre_trained_model

    def build_decoder_model(self):
        X = Input(shape = (self.input_size, ))
        Y = Dense(128, activation = 'relu')(X)
        Y = Dense(128, activation = 'relu')(Y)
        Y = Dense(128, activation = 'relu')(Y)
        Y = Dense(128, activation = 'relu')(Y)
        Y = Dense(128, activation = 'relu')(Y)
        Y = Dense(128, activation = 'relu')(Y)
        Y = Dense(self.output_size, activation = 'linear')(Y)
        model = Model(inputs = [X], outputs = [Y])
        model.compile(loss = 'mean_squared_error', optimizer = self.full_training_optimizer, metrics = ['accuracy'])
        return model

    def build_full_model(self, encoder_weights, decoder_weights, encoder_import, decoder_import, lambda_value):
        opt = self.full_training_optimizer
        a = 5
        b = 100
        X = Input(shape = (self.input_size, ))
        Y = Dense(128, activation = 'relu')(X)
        Y = Dense(64, activation = 'relu')(Y)
        EV = Dense(self.input_size, activation = custom_sigmoid, name = 'embeddedVector')(Y)
        Z = Multiply()([X, EV])

        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(self.output_size, activation = 'linear')(Z)
    
        model = Model(inputs = [X], outputs = [Z])
        model.add_loss(lambda_value * K.sum(K.mean(EV, axis = 0)) / self.input_size)
        model.compile(optimizer=opt, loss=custom_loss(model, 1 - lambda_value), metrics = ['accuracy'])
        
        if encoder_import:
            model.layers[1].set_weights([encoder_weights[0], encoder_weights[1]])
            model.layers[2].set_weights([encoder_weights[2], encoder_weights[3]])
            model.layers[3].set_weights([encoder_weights[4], encoder_weights[5]])
        
        if decoder_import:
            model.layers[5].set_weights( [decoder_weights[0], decoder_weights[1]])
            model.layers[6].set_weights( [decoder_weights[2], decoder_weights[3]])
            model.layers[7].set_weights( [decoder_weights[4], decoder_weights[5]])
            model.layers[8].set_weights( [decoder_weights[6], decoder_weights[7]])
            model.layers[9].set_weights( [decoder_weights[8], decoder_weights[9]])
            model.layers[10].set_weights([decoder_weights[10], decoder_weights[11]])
            model.layers[11].set_weights([decoder_weights[12], decoder_weights[13]])
        
        return model
    
class Optimizer():
    def __init__(self, parent=None):
        self.parent = parent
        
        self.dataset = {}
        
    def set_dataset(self, dataset, header, type):
        self.dataset[header+"_"+type] = copy.deepcopy(dataset)
        
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
        
        
    def start_optimization(self):
        if "training_input" not in self.dataset or len(self.dataset["training_input"]) == 0:
            CustomMessageBox.critical(self.parent, "Optimization error", "No training input data selected.")
            return
        
        if "training_output" not in self.dataset or len(self.dataset["training_output"]) == 0:
            CustomMessageBox.critical(self.parent, "Optimization error", "No training output data selected.")
            return
        
        if "validation_input" not in self.dataset or len(self.dataset["validation_input"]) == 0:
            CustomMessageBox.critical(self.parent, "Optimization error", "No validation input data selected.")
            return
        
        if "validation_output" not in self.dataset or len(self.dataset["validation_output"]) == 0:
            CustomMessageBox.critical(self.parent, "Optimization error", "No validation output data selected.")
            return
        
        if len(self.dataset["training_input"]) != len(self.dataset["training_output"]):
            CustomMessageBox.critical(self.parent, "Optimization error", "The length of the training input data does not match the output data.")
            return
        
        if len(self.dataset["validation_input"]) != len(self.dataset["validation_output"]):
            CustomMessageBox.critical(self.parent, "Optimization error", "The length of the validation input data does not match the output data.")
            return
        
        # with tf.device('/gpu:0'):
        # Settings
        epochs = 5000
        full_training_epochs = 5000
        pre_training_learning_rate = 0.001
        full_training_learning_rate = 0.0001
        
        load_encoder_weights = False
        load_decoder_weights = False
        
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
            
            
        training_input, training_output= self.__get_dataset("training", input_locations, output_locations)
        validation_input, validation_output= self.__get_dataset("validation", input_locations, output_locations)
            
        batch_size = np.shape(training_input)[0]
        model_builder = ModelBuilder(
            input_size = np.shape(training_input)[1], 
            output_size = np.shape(training_output)[1], 
            pre_training_learning_rate = pre_training_learning_rate, 
            full_training_learning_rate = full_training_learning_rate
        )
            
        # pre_trained_encoder_model = model_builder.build_encoder_model()
        # pre_trained_encoder_model.fit(x_train, np.full(np.shape(x_train), 1), epochs = epochs, batch_size = np.size(x_train, 0), verbose = 0, callbacks = [pre_modelCallback])
        # encoder_weights = pre_trained_encoder_model.get_weights()
            
            # # Training
            # model =  model_builder.build_full_model(encoder_weights, [], True, False, 50)
            # model.fit(x_train, y_train, epochs = 1000, batch_size = batchSize, verbose = 0, callbacks = [modelCallback])
            # weights = model.get_weights()

            # model =  model_builder.build_full_model(weights[0:6], weights[6:20], True, True, 100)
            # model.fit(x_train, y_train, epochs = 1000, batch_size = batchSize, verbose = 0, callbacks = [modelCallback])
            # weights = model.get_weights()

            # model =  model_builder.build_full_model(weights[0:6], weights[6:20], True, True, 200)
            # model.fit(x_train, y_train, epochs = 1000, batch_size = batchSize, verbose = 0, callbacks = [modelCallback])
            # weights = model.get_weights()
            
            # # model =  model_builder.build_full_model(weights[0:6], weights[6:20], True, True, 150)
            # # model.fit(x_train, y_train, epochs = 1000, batch_size = batchSize, verbose = 0, callbacks = [modelCallback])
            # # weights = model.get_weights()
            
            # # model =  model_builder.build_full_model(weights[0:6], weights[6:20], True, True, 200)
            # # model.fit(x_train, y_train, epochs = 1000, batch_size = batchSize, verbose = 0, callbacks = [modelCallback])
            # # weights = model.get_weights()
            
            # # model =  model_builder.build_full_model(weights[0:6], weights[6:20], True, True, 300)
            # # model.fit(x_train, y_train, epochs = 1000, batch_size = batchSize, verbose = 0, callbacks = [modelCallback])
            
            
            # # Save training results
            # training_result = np.vstack((
            #     np.array(input_locations),
            #     variable_into_padded_array(pre_training_learning_rate, shape = (np.size(input_locations, 0), )),
            #     variable_into_padded_array(full_training_learning_rate, shape = (np.size(input_locations, 0), )),
            #     variable_into_padded_array(interface.execution_time, shape = (np.size(input_locations, 0), )),
            #     modelCallback.get_stacked_arr()
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