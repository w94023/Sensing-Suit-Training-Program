from lib.base import *
from lib.pyqt_base import *

from lib.scr.csv import *
from lib.scr.pyqt import *
from lib.scr.json import *

import tensorflow as tf
# from tensorflow import keras
from keras import optimizers
from keras.layers import Input, Dense, Multiply, Layer
from keras.models import Model
import keras.backend as K
import h5py

import struct

def __set_gpu_memory_growth():
    # tensorflow가 gpu 메모리 할당 시, 필요한 메모리 점진적으로 증가하도록 설정
    # gpu 메모리 부족으로 인한 오류 시 사용
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            # CustomMessageBox.critical(self.parent, "Optimization error", "Failed to configure GPU memory.")
            print(e)

__set_gpu_memory_growth()

def convert_to_float_or_str(value):
    # 정규식을 사용하여 float 형식인지 확인
    if re.match(r"^[+-]?(\d+(\.\d*)?|\.\d+)$", value):
        return float(value)
    else:
        return value

# def import_csv_file(file_path, skiprows=0, skipcols=0):
#     if file_path.exists():
#         df_temp = pd.read_csv(file_path, skiprows=skiprows, header=None)
#         df = pd.read_csv(file_path, skiprows=skiprows, usecols = list(range(skipcols, df_temp.shape[1])), header=None)
#         return df
#     else:
#         print("Failed to load csv file : " + str(file_path))
#         return None
    
current_directory = os.path.dirname(os.path.abspath(__file__))
data = import_csv_file(Path(os.path.join(current_directory, "Test.csv")))

optimization_result = {}
optimization_result["pre training epoch"] = data.iloc[0, 2]
optimization_result["pre training learning rate"] = data.iloc[0, 4]
optimization_result["full training epoch"] = data.iloc[0, 6]
optimization_result["full training learning rate"] = data.iloc[0, 8]
optimization_result["lambda 1"] = data.iloc[1, 2]
optimization_result["lambda 2"] = data.iloc[1, 3]
optimization_result["lambda 3"] = data.iloc[1, 4]
optimization_result["execution time"] = data.iloc[2, 2]
optimization_result["output location"] = data.iloc[4, 2:].dropna().tolist()
optimization_result["input location"] = data.iloc[6, 2:].dropna().tolist()
optimization_result["time hist"] = data.iloc[7:, 1].dropna().tolist()
optimization_result["embedded vector hist"] = data.iloc[7:, 2:].dropna().to_numpy()

print('csv import done')

opt = optimizers.Adam(learning_rate = 0.001, beta_1 = 0.9, beta_2 = 0.999, epsilon = None, decay = 0)
# # 간단한 모델 정의
X = Input(shape = (5, ))
Y = Dense(128, activation = 'relu')(X)
Y = Dense(64, activation = 'relu')(Y)
Y = Dense(5, activation = 'linear')(Y)
pre_trained_model = Model(inputs = [X], outputs = [Y])
pre_trained_model.compile(loss = 'mean_squared_error', optimizer = opt, metrics = ['accuracy'])


# # 모델을 HDF5 파일로 저장
model_path = os.path.join(current_directory, "Test.h5")
pre_trained_model.save(model_path)

# h5py를 사용하여 dictionary 데이터를 같은 파일에 추가
with h5py.File(model_path, 'a') as f:
    # dictionary의 각 항목을 HDF5 파일에 저장
    for key, value in optimization_result.items():
        if isinstance(value, str):
            # 문자열은 UTF-8로 인코딩하여 저장
            dt = h5py.string_dtype(encoding='utf-8')
            dataset = f.create_dataset(key, (1,), dtype=dt)
            dataset[0] = value
        elif isinstance(value, (int, float)):
            # 스칼라 값은 배열 형태로 저장
            f.create_dataset(key, data=np.array(value))
        elif isinstance(value, list):
            if all(isinstance(item, str) for item in value):
                # 문자열 리스트인 경우 UTF-8로 인코딩하여 저장
                dt = h5py.string_dtype(encoding='utf-8')
                f.create_dataset(key, data=np.array(value, dtype=dt))
            else:
                # 정수나 실수 리스트인 경우 일반 배열로 저장
                f.create_dataset(key, data=np.array(value))
        
print('h5 export done')

# TensorFlow 모델 불러오기
model = tf.keras.models.load_model(model_path)

# h5py를 사용하여 추가 데이터 불러오기
extra_data = {}
with h5py.File(model_path, 'r') as f:
    # 모델과는 별도로 저장된 extra_data를 불러오기
    for key in f.keys():
        if key not in model.layers:  # 모델 레이어 이름이 아닌 키만 추가
            # 데이터셋인 경우 값 읽기
            if isinstance(f[key], h5py.Dataset):
                data = f[key][()]

                # 데이터가 바이트 문자열 배열인 경우
                if isinstance(data, (np.void, np.ndarray)):
                    data = np.array([convert_to_float_or_str(item.decode('utf-8')) for item in data])

                # 단일 바이트 문자열인 경우
                elif isinstance(data, bytes):
                    data = data.decode('utf-8')
                    
                extra_data[key] = data

print("\nExtra Data Loaded:")
print(extra_data["pre training epoch"])