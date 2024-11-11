from ...pyqt_base import *

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
        # DataFrame을 CSV로 저장
        data.to_csv(file_path, index=False)
    else:
        CustomMessageBox.critical(parent, "CSV data export error", "Invalid save path.")
        
        
def __load_marker_csv_file_data(file_path, parent):
    """Marker 타입으로 인식된 CSV파일의 데이터 불러오는 메서드

    Args:
        file_path (str): Import 대상 CSV 파일 경로
        parent (QWidget): 부모 위젯. Default to None

    Returns:
        (pd.DataFrame): Import 결과 데이터, 데이터 읽기에 실패했을 경우 None 반환
    """

    df = import_csv_file(file_path, 7, 1)
    
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