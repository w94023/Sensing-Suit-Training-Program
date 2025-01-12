import tensorflow as tf
import h5py

# 간단한 모델 정의
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(32,)),
    tf.keras.layers.Dense(10, activation='softmax')
])

# 모델 저장 경로
model_path = "model_with_data.h5"

# 모델을 HDF5 파일로 저장
model.save(model_path)

# 추가적으로 저장할 dictionary 데이터
extra_data = {
    "param1": 0.5,
    "param2": 10,
    "param3": [1, 2, 3, 4, 5]
}

# h5py를 사용하여 dictionary 데이터를 같은 파일에 추가
with h5py.File(model_path, 'a') as f:
    # dictionary의 각 항목을 HDF5 파일에 저장
    for key, value in extra_data.items():
        f.create_dataset(key, data=value)