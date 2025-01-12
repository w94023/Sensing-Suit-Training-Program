from ...pyqt_base import *
from ...ui_common import *
from ...nn_base import *
from ..pyqt import *
from ..thread import *

from ..pyqt.widget import (CustomMessageBox)

import tensorflow as tf
# from tensorflow import keras
from keras import optimizers
from keras.layers import Input, Dense, Multiply, Layer
from keras.models import Model
import keras.backend as K

def set_gpu_memory_growth(parent=None):
        # tensorflow가 gpu 메모리 할당 시, 필요한 메모리 점진적으로 증가하도록 설정
        # gpu 메모리 부족으로 인한 오류 시 사용
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
            except RuntimeError as e:
                CustomMessageBox.critical(parent, "Optimization error", "Failed to configure GPU memory.")
                
def set_gpu_memory_strict(memory_size, parent=None):
    # tensorflow가 gpu 메모리 할당 시, 제한된 메모리만 사용하도록 설정
    # memory_size : MB 단위, 4GB 제한 시 4096 입력 필요
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            tf.config.set_logical_device_configuration(
                gpus[0],
                [tf.config.LogicalDeviceConfiguration(memory_limit=memory_size)])
        except RuntimeError as e:
            CustomMessageBox.critical(parent, "Optimization error", "Failed to configure GPU memory.")
            
def get_dataset(dataset, header, input_locations, output_locations, get_time_label=False):
    # get_time_label = True일 경우, input으로부터 time열 추출하여 반환
    if get_time_label:
        time_dataset = pd.DataFrame()
        
    input_dataset = pd.DataFrame()
    for data in dataset[header+"_input"].values():
        extracted_data = data[input_locations]
        input_dataset = pd.concat([input_dataset, extracted_data], axis=0, ignore_index=True)
        
        if get_time_label:
            time_data = data["Time (s)"]
            time_dataset = pd.concat([time_dataset, time_data], axis=0, ignore_index=True)
        
    output_dataset = pd.DataFrame()
    for data in dataset[header+"_output"].values():
        extracted_data = data[output_locations]
        output_dataset = pd.concat([output_dataset, extracted_data], axis=0, ignore_index=True)
        
    if get_time_label:
        return input_dataset.to_numpy(), output_dataset.to_numpy(), time_dataset.to_numpy()
    else:
        return input_dataset.to_numpy(), output_dataset.to_numpy()