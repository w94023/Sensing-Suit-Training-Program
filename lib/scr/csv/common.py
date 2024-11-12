from ...pyqt_base import *
import csv
from enum import Enum

class DataType(Enum):
    MotiveExportedMarkerData = 1
    RefinedMarkerData = 2

number_of_wireframe_marker = 34
number_of_axis_marker = 3
number_of_joint_marker = 2

def load_csv_file(file_path, file_type, parent=None):
    """CSV에서 import한 데이터 pd.DataFrame으로 반환하는 메서드

    Args:
        file_path (str): Import 대상 CSV 파일 경로
        file_type (str): CSV 파일 타입 ("marker" or "sensor")
        parent (QWidget): 부모 위젯. Default to None

    Returns:
        (pd.DataFrame): Import 결과 데이터, 데이터 읽기에 실패했을 경우 None 반환
    """
    
    if file_type == "marker":
        return __load_marker_csv_file_data(Path(file_path), parent)
    elif file_type == "sensor":
        return __load_sensor_csv_file_data(Path(file_path), parent)
    else:
        CustomMessageBox.critical(parent, "CSV data import error", "The data type is invalid (it must be recognized as either a marker or a sensor).")
        return None
        
def save_csv_file(file_path, data, parent=None):
    if file_path:
        # 7개의 빈 행과 1개의 빈 열 추가
        empty_rows = [[""] * (len(data.columns) + 1)] * 6
        empty_rows.append([""]+list(data.columns))
        empty_df = pd.DataFrame(empty_rows, columns=[""] + list(data.columns))
        df_with_empty = pd.concat([empty_df, data], ignore_index=True)

        # DataFrame을 CSV로 저장
        df_with_empty.to_csv(file_path, index=False, header=False)
    else:
        CustomMessageBox.critical(parent, "CSV data export error", "Invalid save path.")

def __type_classifier(data_2d_list):
    # 최대 열 크기 계산
    max_columns = max(len(row) for row in data_2d_list)

    # 파일 타입
    df_type = None

    # 행 1, 열 1의 성분으로 CSV 파일 타입 검사
    if data_2d_list[0][0] == "Format Version":
        # row 선택
        selected_rows = data_2d_list[7:]
        # column 선택
        selected_columns = list(range(1, max_columns))
        # 열 이름 선택
        column_names = [data_2d_list[6][i] for i in selected_columns]
        df_type = DataType.MotiveExportedMarkerData
    else:
        # row 선택
        selected_rows = data_2d_list[7:]
        # column 선택
        selected_columns = list(range(1, max_columns))
        # 열 이름 선택
        column_names = [data_2d_list[6][i] for i in selected_columns]
        df_type = DataType.RefinedMarkerData

    # 슬라이싱된 데이터를 기반으로 새로운 리스트 생성
    filtered_data = [[row[i] for i in selected_columns] for row in selected_rows]

    # DataFrame으로 변환
    df = pd.DataFrame(filtered_data, columns=column_names, dtype=float)

    return df, df_type

def __create_custom_index_list(length):
    # Motive에서 마커 데이터 추출 시 각 열의 마커 인덱스를 생성하는 리스트
    # ex. 1, 10, 11, ... ,19, 2, 20, 21, ..., 29, 3, 30, ...
    
    custom_list = []
    i = 1  # 초기 숫자 (1부터 시작)

    while len(custom_list) < length:
        # 1. 첫 번째 요소 추가 (1, 2, 3, ... 순서)
        if i <= length:
            custom_list.append(i)
        
        # 2. 10*i ~ 10*i + 9 범위의 숫자 추가
        range_start = 10 * i
        range_end = min(10 * i + 9, length)  # 범위가 length를 넘지 않도록 제한
        custom_list.extend(range(range_start, range_end + 1))

        i += 1  # 다음 숫자로 넘어감
    
    # 리스트 길이가 초과될 수 있으므로 필요한 길이까지만 자름
    return custom_list[:length]

def __load_marker_csv_file_data(file_path, parent):
    """Marker 타입으로 인식된 CSV파일의 데이터 불러오는 메서드

    Args:
        file_path (str): Import 대상 CSV 파일 경로
        parent (QWidget): 부모 위젯. Default to None

    Returns:
        (pd.DataFrame): Import 결과 데이터, 데이터 읽기에 실패했을 경우 None 반환
    """

    # 첫 7개 행, 첫 1개 열 버림
    # df = pd.read_csv(file_path, skiprows=7, header=None).iloc[:, 1:]

    # 2D 리스트로 CSV 파일 읽기
    data_2d_list = []

    # CSV 파일 열기 및 읽기
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)  # csv.reader로 파일을 읽음
        for row in csvreader:
            data_2d_list.append(row)  # 각 행을 2D 리스트에 추가

    # 데이터 pd.DataFrame으로 변환 및 타입 분류
    df, df_type = __type_classifier(data_2d_list)

    if df_type == DataType.MotiveExportedMarkerData:
        if (df.shape[1]-1) % 3 != 0:
            CustomMessageBox.critical(parent, "CSV data import error", "The number of columns is not a multiple of 3")
            return None
    
        motive_marker_index = __create_custom_index_list(number_of_wireframe_marker)

        # 정렬 후 각 멤버의 원래 인덱스도 함께 반환
        reclassified_with_indices = sorted(enumerate(motive_marker_index), key=lambda x: x[1])

        # 원래 인덱스를 분리하여 출력
        original_indexes = [index for index, value in reclassified_with_indices]

        # df와 동일한 크기의 빈 DataFrame 생성
        df_output = pd.DataFrame(np.nan, index=df.index, columns=df.columns)
        df_output.iloc[:, 0] = df.iloc[:, 0]

        output_col_count = 0
        # wireframe marker 데이터 저장
        for original_index in original_indexes:
            # +1 : 첫 열 제외 (time)
            df_output.iloc[:, 3*output_col_count+0 + 1] = df.iloc[:, 3*original_index+0 + 1] # X
            df_output.iloc[:, 3*output_col_count+1 + 1] = df.iloc[:, 3*original_index+1 + 1] # Y
            df_output.iloc[:, 3*output_col_count+2 + 1] = df.iloc[:, 3*original_index+2 + 1] # Z
            output_col_count += 1

        # axis marker 및 joint makrer 데이터 저장
        for i in range(number_of_axis_marker + number_of_joint_marker):
            # +1 : 첫 열 제외 (time)
            df_output.iloc[:, 3*output_col_count+0 + 1] = df.iloc[:, 3*output_col_count+0 + 1] # X
            df_output.iloc[:, 3*output_col_count+1 + 1] = df.iloc[:, 3*output_col_count+1 + 1] # Y
            df_output.iloc[:, 3*output_col_count+2 + 1] = df.iloc[:, 3*output_col_count+2 + 1] # Z
            output_col_count += 1

        column_labels = ["Time (s)"]
        for i in range((df.shape[1]-1)//3):
            column_labels.append("Marker"+str(i+1)+"X")
            column_labels.append("Marker"+str(i+1)+"Y")
            column_labels.append("Marker"+str(i+1)+"Z")
        df_output.columns = column_labels

        return df_output
    
    else:
        if (df.shape[1]-1) % 3 != 0:
            CustomMessageBox.critical(parent, "CSV data import error", "The number of columns is not a multiple of 3")
            return None
        
        column_labels = ["Time (s)"]
        for i in range((df.shape[1]-1)//3):
            column_labels.append("Marker"+str(i+1)+"X")
            column_labels.append("Marker"+str(i+1)+"Y")
            column_labels.append("Marker"+str(i+1)+"Z")
        df.columns = column_labels
        
        return df
        
def __load_sensor_csv_file_data(file_path, parent):
    """Sensor 타입으로 인식된 CSV파일의 데이터 불러오는 메서드

    Args:
        file_path (str): Import 대상 CSV 파일 경로
        parent (QWidget): 부모 위젯. Default to None

    Returns:
        (pd.DataFrame): Import 결과 데이터, 데이터 읽기에 실패했을 경우 None 반환
    """

    df = import_csv_file(file_path, 0, 0)
    
    if df.shape[1] < 2:
        CustomMessageBox.critical(parent, "Data import error", "The file does not contain sensor data")
        return None
    
    column_labels = ["Time (ms)"]
    for i in range(df.shape[1]-1):
        column_labels.append("Sensor"+str(i+1))
    df.columns = column_labels
    
    return df