from .common import *

class ModelBuilder():
    def __init__(self, input_size, output_size, pre_training_learning_rate, full_training_learning_rate):
        self.input_size = input_size
        self.output_size = output_size
        self.pre_training_optimizer = optimizers.Adam(learning_rate = pre_training_learning_rate, beta_1 = 0.9, beta_2 = 0.999, epsilon = None, decay = 0)
        self.full_training_optimizer = optimizers.Adam(learning_rate = full_training_learning_rate, beta_1 = 0.9, beta_2 = 0.999, epsilon = None, decay = 0)
        
    def __custom_sigmoid(self, x):
        condition = K.greater_equal(x, 0.0)
        return K.switch(condition, K.tanh(x), tf.zeros_like(x))

    def __custom_loss(self, model, alpha):
        def loss(y_true, y_pred):
            # Mean squared error
            # mse = K.mean(K.square(y_pred - y_true), axis=-1)
            # rmse = K.sqrt(mse)  # RSME 계산
            mae = K.mean(K.abs(y_pred - y_true), axis=-1)
            # capped_mse = K.minimum(mae, 100.0)
            # 최종 손실 계산
            return mae * alpha
        return loss

    def build_encoder_model(self):
        X = Input(shape = (self.input_size, ))
        Y = Dense(128, activation = 'relu')(X)
        Y = Dense(64, activation = 'relu')(Y)
        Y = Dense(self.input_size, activation = 'linear')(Y)
        pre_trained_model = Model(inputs = [X], outputs = [Y])
        pre_trained_model.compile(loss = 'mean_squared_error', optimizer = self.pre_training_optimizer, metrics = ['accuracy'])
        return pre_trained_model

    def build_full_model(self, encoder_weights, decoder_weights, encoder_import, decoder_import, lambda_value):
        opt = self.full_training_optimizer
        a = 5
        b = 100
        X = Input(shape = (self.input_size, ))
        Y = Dense(128, activation = 'relu')(X)
        Y = Dense(64, activation = 'relu')(Y)
        EV = Dense(self.input_size, activation = self.__custom_sigmoid, name = 'embeddedVector')(Y)
        Z = Multiply()([X, EV])

        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(128, activation = 'relu')(Z)
        Z = Dense(self.output_size, activation = 'linear')(Z)
    
        model = Model(inputs = [X], outputs = [Z])
        # model.add_loss(lambda_value * K.sum(K.mean(EV, axis = 0)) / self.input_size)
        model.add_loss(lambda_value * K.sum(K.mean(EV, axis = 0)))
        model.compile(optimizer=opt, loss = self.__custom_loss(model, 1 - lambda_value), metrics = ['accuracy'])
        
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
    