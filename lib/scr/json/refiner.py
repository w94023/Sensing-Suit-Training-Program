from .common import *
import copy

class WorkerThread(BackgroundThreadWorker):
    finished = pyqtSignal(bool, int, int, dict, dict, Exception)  # 작업 완료 시그널

    def __init__(self, json_data_manager, target_data_keys, marker_labels, window_size, progress_dialog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_data_manager = json_data_manager
        self.target_data_keys = target_data_keys

        # Marker refining 시 기준 마커 label 저장
        self.coordinate_marker_1_label = marker_labels[0]
        self.coordinate_marker_2_label = marker_labels[1]
        self.coordinate_marker_3_label = marker_labels[2]

        # Sensor refining 시 window size 저장
        self.window_size = window_size

        # Progress 표시할 창 저장
        self.progress_dialog = progress_dialog

        # Marker, sensor 작업의 progress 비중 저장
        # 일반적으로 marker 작업이 더 오래 걸리기 때문에, marker에 더 높은 가중치 설정
        # ex. 0.8 : 마커 작업 완료 시 80%, 센서 작업 완료 시 20% 할당
        self.marker_sensor_progress_ratio = 0.95

    # def __normalize_vector(self, v):
    #     # 벡터의 크기 (norm) 계산
    #     norm = np.linalg.norm(v)
    #     # 벡터 정규화
    #     if norm != 0:
    #         normalized_v = v / norm
    #     else:
    #         normalized_v = v  # 벡터의 크기가 0인 경우 정규화를 하지 않음
    #     return normalized_v
    
    def __normalize_vector(self, vectors):
        """
        벡터 배열을 받아 모든 벡터를 정규화하는 함수.
        vectors: np.array of shape (n, 3) (n개의 3D 벡터 배열)
        """
        norms = np.linalg.norm(vectors, axis=1)
        # 크기가 0이 아닌 벡터만 정규화하고, 0인 경우 원래 값을 유지
        normalized_vectors = np.divide(vectors.T, norms, where=norms != 0).T
        return normalized_vectors
    
    def __refine_marker_data(self, key, index, total_count, df):
        p1_index = find_column_from_label(df, self.coordinate_marker_1_label)
        p2_index = find_column_from_label(df, self.coordinate_marker_2_label)
        p3_index = find_column_from_label(df, self.coordinate_marker_3_label)
        
        if len(p1_index) < 3 or len(p2_index) < 3 or len(p3_index) < 3:
            return None, Exception(f"The coordinate marker is not included in the marker data : {key}")
        
        if len(p1_index) > 3 or len(p2_index) > 3 or len(p3_index) > 3:
            return None, Exception(f"There are too many markers with the name 'coordinate marker' in the marker data : {key}")
        
        row_num = df.shape[0]
        marker_num = int((df.shape[1]-1)/3)
        
        for i in range(df.shape[0]):
            """
            주어진 인덱스의 행에서 p1, p2, p3 벡터를 사용하여 변환 행렬을 만들고,
            각 포인트 데이터에 변환 행렬을 적용하는 최적화된 연산 수행.
            """
            
            # 반복되는 연산 최소화, numpy의 벡터화 연산 최대한 사용, DataFrame의 값을 한 번에 업데이트
    
            # p1 : 몸통 아래쪽 마커
            # p2 : 몸통 중앙 마커
            # p3 : 몸통 팔쪽 마커
            p1 = df.iloc[i, p1_index].to_numpy() # 아래쪽
            p2 = df.iloc[i, p2_index].to_numpy() # 중앙
            p3 = df.iloc[i, p3_index].to_numpy() # 팔쪽
            
            # z_vector = self.__normalize_vector(p3 - p2)
            # y_vector_temp = p2 - p1
            # x_vector = self.__normalize_vector(np.cross(y_vector_temp, z_vector))
            # y_vector = self.__normalize_vector(np.cross(z_vector, x_vector))
            
            # 벡터 연산을 numpy 배열로 한 번에 계산
            z_vector = self.__normalize_vector(np.array([p3 - p2]))[0]
            y_vector_temp = p2 - p1
            x_vector = self.__normalize_vector(np.array([np.cross(y_vector_temp, z_vector)]))[0]
            y_vector = self.__normalize_vector(np.array([np.cross(z_vector, x_vector)]))[0]
    
            # 변환 행렬 생성 (벡터들을 새로운 좌표축으로 정렬)
            transformation_matrix = np.array([x_vector, y_vector, z_vector]).T  # 3x3 행렬
            
            # 전체 좌표 데이터 추출 및 변환
            coords = np.array([df.iloc[i, [j * 3 + 1, j * 3 + 2, j * 3 + 3]].to_numpy() for j in range(marker_num)])
            transformed_coords = np.dot(coords - p2, transformation_matrix)

            # 결과를 DataFrame에 한 번에 저장
            for j in range(marker_num):
                df.iloc[i, [j * 3 + 1, j * 3 + 2, j * 3 + 3]] = transformed_coords[j]
                
            self.update_progress((i / (row_num - 1)) * ((index + 1) / total_count) * self.marker_sensor_progress_ratio * 100)
            
            # flag 변경 시 작업 중도 정지
            if not self._is_running:
                return None, Exception("The operation was canceled by the user.")

        return df, Exception()

    def __refine_sensor_data(self, key, index, total_count, df):
        # Time 열만 있는 경우
        if (df.shape[1] < 2):
            return None, Exception(f"There is only Time data in the sensor data column : {key}")

        # Time 열을 second 단위로 변환
        df["Time (ms)"].astype(float)
        df["Time (ms)"] = df["Time (ms)"] / 1000
        df.rename(columns={"Time (ms)": "Time (s)"}, inplace=True)

        # Sensor 열에 smoothing 적용
        sensor_num = df.shape[1]-1
        for i in range(sensor_num):
            df["Sensor"+str(i+1)] = df["Sensor"+str(i+1)].rolling(window=self.window_size).mean()
            
            self.update_progress((i/(sensor_num-1))*((index+1)/total_count)*(1-self.marker_sensor_progress_ratio)*100 + self.marker_sensor_progress_ratio*100)
            
            # flag 변경 시 작업 중도 정지
            if not self._is_running:
                return None, Exception("The operation was canceled by the user.")

        _, refined_df = split_dataframe(df, self.window_size-1)
        refined_df["Time (s)"] = refined_df["Time (s)"]-refined_df["Time (s)"][0]
        return refined_df.astype(float), Exception()

    def run(self):
        # target count 대비 success count 계산을 위한 변수 선언
        target_count = len(self.target_data_keys)
        success_count = 0

        target_data = self.json_data_manager.file_data

        if target_data is None:
            self.finished.emit(False, 0, target_count, {}, {}, Exception("No file has been selected."))

        else:
            marker_data_list = {}
            marker_refined_data_list = {}
            sensor_data_list = {}
            sensor_refined_data_list = {}
            
            for target_data_key in self.target_data_keys:
                # list형태의 key를 string으로 변환
                # ex. ['AA', 'marker', 'raw'] > 'AA-marker-row'
                key = "-".join(target_data_key)

                # target으로 설정된 데이터 명이, 현재 로드된 JSON 파일의 데이터에 없을 경우 loop 스킵
                if key not in target_data.keys():
                    continue

                # target 데이터가 마커 데이터인 경우
                if "marker-raw" in key:
                    refined_key = key.split("-")
                    refined_key[2] = "refined"
                    refined_key = "-".join(refined_key)

                    marker_data_list[refined_key] = copy.deepcopy(target_data[key])

                # target 데이터가 센서 데이터인 경우
                if "sensor-raw" in key:
                    refined_key = key.split("-")
                    refined_key[2] = "refined"
                    refined_key = "-".join(refined_key)

                    sensor_data_list[refined_key] = copy.deepcopy(target_data[key])

            count = 0
            for key, marker_data in marker_data_list.items():
                refined_marker_data, exception = self.__refine_marker_data(key, count, len(marker_data_list), pd.DataFrame(marker_data))
                if refined_marker_data is None:
                    self.finished.emit(False, success_count, target_count, {}, {}, exception)
                    return
                else:
                    marker_refined_data_list[key] = refined_marker_data
                    count += 1
                    success_count += 1

            count = 0
            for key, sensor_data in sensor_data_list.items():
                refined_sensor_data, exception = self.__refine_sensor_data(key, count, len(sensor_data_list), pd.DataFrame(sensor_data))
                if refined_sensor_data is None:
                    self.finished.emit(False, success_count, target_count, {}, {}, exception)
                    return
                else:
                    sensor_refined_data_list[key] = refined_sensor_data
                    count += 1
                    success_count += 1

            self.finished.emit(True, success_count, target_count, marker_refined_data_list, sensor_refined_data_list, Exception())
                
class DataRefiner():
    def __init__(self, json_data_manager, parent=None):
        self.parent = parent

        # JSON 데이터 보관 인스턴스 저장
        self.json_data_manager = json_data_manager

        # 스레드 관리
        self.refining_thread = None
        
        # 오래 걸리는 작업 표시를 위한 loading dialog 생성
        self.progress_dialog = ProgressDialog("Data refining progress", self.parent)

        # coordinate marker 등록
        self.coordinate_marker_1_label = "Marker1"
        self.coordinate_marker_2_label = "Marker2"
        self.coordinate_marker_3_label = "Marker3"

        # Sensor data smoothing window size 설정
        self.window_size = 5

    def refine_data(self, target_data_keys):
        # 이전 작업이 진행 중일 경우
        if self.refining_thread is not None:
            CustomMessageBox.critical(self.parent, "Error", "The previous data refining task has not been completed.")
            return
        
        # 파일이 선택되지 않았을 경우
        if target_data_keys is None:
            CustomMessageBox.critical(self.parent, "Error", "No file has been selected.")
            return
        
        # 파일이 선택되지 않았을 경우
        if len(target_data_keys) == 0:
            CustomMessageBox.critical(self.parent, "Error", "No file has been selected.")
            return
        
        # 작업 시작 window 표시
        self.progress_dialog.start_progress()

        # 작업 스레드 시작
        self.refining_thread = WorkerThread(self.json_data_manager,
                                            target_data_keys,[
                                                self.coordinate_marker_1_label,
                                                self.coordinate_marker_2_label,
                                                self.coordinate_marker_3_label
                                            ],
                                            self.window_size,
                                            self.progress_dialog)
        self.refining_thread.finished.connect(self.__on_refining_finished)
        self.progress_dialog.set_worker(self.refining_thread) # 백그라운드 스레드 전달
        self.refining_thread.start()

    def __on_refining_finished(self, is_succeed, success_count, target_count, marker_refined_data, sensor_refined_data, exception):
        # 작업 종료 window 표시
        self.progress_dialog.stop_progress()

        if not is_succeed:
            CustomMessageBox.critical(self.parent, "Error", f"Failed to refine the data : {exception}")
        else:
            for key, value in marker_refined_data.items():
                self.json_data_manager.add_data_to_target_json_file(key, value)
            for key, value in sensor_refined_data.items():
                self.json_data_manager.add_data_to_target_json_file(key, value)  
            CustomMessageBox.information(self.parent, "Information", f"Data refining has been completed : {success_count} / {target_count}")

        self.refining_thread = None
        self.progress_dialog.set_worker(self.refining_thread) # 백그라운드 스레드 전달
          
# class DataRefiningWidget(QWidget):
#     def __init__(self, json_data_manager, json_data_viewer, parent=None):
#         super().__init__(parent)
        
#         self.parent= parent
        
#         # JSON data 관리 인스턴스 저장
#         self.json_data_manager = json_data_manager
#         self.json_data_viewer = json_data_viewer
        
#         # # Data refiner 저장
#         self.data_refiner = DataRefiner(self.json_data_manager)
        
#         # JSON data 목록 클릭 이벤트 등록
#         self.json_data_viewer.on_item_clicked += self.__on_target_data_changed
        
#         # UI 초기화
#         self.init_ui()
        
#         # Target data list 저장
#         self.target_data_list = []
 
#     def init_ui(self):

#         def __set_label_style(label, height):
#             label.setFixedSize(0, height)
#             label.setMinimumSize(0, height)
#             label.setMaximumSize(16777215, height)
#             label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
#             label.setStyleSheet(f"""
#                                  background-color: {UiStyle.get_color("background_color")};
#                                  color: {UiStyle.get_color("content_text_color")};
#                                  font-family: {UiStyle.text_font};
#                                  """)
            
#         def __set_text_field_style(text_field, height):
#             text_field.setFixedSize(0, height)
#             text_field.setMinimumSize(0, height)
#             text_field.setMaximumSize(16777215, height)
#             text_field.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
#             text_field.setStyleSheet(f"""
#                                       background-color: {PyQtAddon.get_color("background_color")};
#                                       color: {PyQtAddon.get_color("content_text_color")};
#                                       font-family: {PyQtAddon.text_font};
#                                       border: 1px solid {PyQtAddon.get_color("content_line_color")};
#                                       """)
            
#         def __set_custom_line_edit_style(custom_line_edit, height, default_text):
#             custom_line_edit.setFixedSize(0, height)
#             custom_line_edit.setMinimumSize(0, height)
#             custom_line_edit.setMaximumSize(16777215, height)
#             custom_line_edit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
#             custom_line_edit.set_text_in_line_edit(default_text) # 기본값 설정

#         def __set_button_style(button, height):
#             button.setFixedSize(0, height)
#             button.setMinimumSize(0, height)
#             button.setMaximumSize(16777215, height)
#             button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
#             button.setStyleSheet(f"""
#                                   QPushButton {{
#                                       background-color: {PyQtAddon.get_color("point_color_1")};
#                                       color: {PyQtAddon.get_color("content_text_color")};
#                                       padding: 4px 8px;
#                                       border-radius: 0px;
#                                       border: none;
#                                   }}
#                                   QPushButton:hover {{
#                                       background-color: {PyQtAddon.get_color("point_color_5")};
#                                       border: none;
#                                   }}
#                                   """)

#         # 레이아웃 생성
#         layout = QVBoxLayout()
#         self.setLayout(layout)
        
#         # Selected file counts label 표시
#         selected_file_count_label = QLabel("Selected file count", self.parent)
#         __set_label_style(selected_file_count_label, 20)
        
#         # Selected file counts text field 표시
#         self.selected_file_count_text_field = QLabel("", self.parent)
#         __set_text_field_style(self.selected_file_count_text_field, 20)
        
#         # Axis marker LineEidt label 표시
#         axis_marker_input_field_label = QLabel("Axis markers", self.parent)
#         __set_label_style(axis_marker_input_field_label, 20)
        
#         # Axis marker 1 input field 생성
#         self.axis_marker_1_input_field = CustomLineEdit(self.__check_axis_marker_1_input, self.parent)
#         __set_custom_line_edit_style(self.axis_marker_1_input_field, 20, "Marker1")
        
#         # Axis marker 2 input field 생성
#         self.axis_marker_2_input_field = CustomLineEdit(self.__check_axis_marker_2_input, self.parent)
#         __set_custom_line_edit_style(self.axis_marker_2_input_field, 20, "Marker2")
        
#         # Axis marker 3 input field 생성
#         self.axis_marker_3_input_field = CustomLineEdit(self.__check_axis_marker_3_input, self.parent)
#         __set_custom_line_edit_style(self.axis_marker_3_input_field, 20, "Marker3")
        
#         # Window size LineEidt label 표시
#         window_size_input_field_label = QLabel("Window size", self.parent)
#         __set_label_style(window_size_input_field_label, 20)
        
#         # Window size input field 생성
#         self.window_size_input_field = CustomLineEdit(self.__check_window_size_input, parent=self.parent)
#         __set_custom_line_edit_style(self.window_size_input_field, 20, "50")
        
#         # QSpacerItem: 빈 공간 생성
#         spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        
#         # QPushButton: 입력된 텍스트를 출력하는 버튼
#         button = QPushButton("Refine data", self.parent)
#         button.clicked.connect(self.refine_data)
#         __set_button_style(button, 20)

#         # 레이아웃에 위젯 추가
#         layout.addWidget(selected_file_count_label)
#         layout.addWidget(self.selected_file_count_text_field)
#         layout.addWidget(axis_marker_input_field_label)
#         layout.addWidget(self.axis_marker_1_input_field)
#         layout.addWidget(self.axis_marker_2_input_field)
#         layout.addWidget(self.axis_marker_3_input_field)
#         layout.addWidget(window_size_input_field_label)
#         layout.addWidget(self.window_size_input_field)
#         # layout.addItem(spacer)
#         layout.addWidget(button)
        
#         # self.setMaximumHeight(300)
#         self.setStyleSheet(f"""
#                             QWidget {{
#                                 margin: 0px;
#                                 padding: 0px;
#                                 background-color: {PyQtAddon.get_color("background_color")};
#                                 }}""")

#     def __clear(self):
#         self.target_data_list.clear()
#         self.selected_file_count_text_field.setText("")

#     def __on_target_data_changed(self, selected_items):
#         # selected item이 없거나, target file이 변경되었을 경우
#         if selected_items is None:
#             self.__clear()
#             return

#         if len(selected_items) == 0:
#             self.__clear()
#             return
        
#         # selected item 저장
#         self.target_data_list = selected_items
        
#         # target file count 표시
#         self.__set_target_file_count(len(self.target_data_list))

#     def __set_target_file_count(self, target_file_count):
#         # target file count 표시
        
#         if target_file_count < 2:
#             self.selected_file_count_text_field.setText(str(target_file_count)+" file")
#         else:
#             self.selected_file_count_text_field.setText(str(target_file_count)+" files")

#     def __check_axis_marker_1_input(self, text):
#         # 입력이 Marker + 숫자 인 지 확인
#         if bool(re.match(r"^Marker\d+$", text)):
#             self.data_refiner.coordinate_marker_1_label = text
#             CustomMessageBox.information(self.parent, "Information", f"The axis marker 1 has been set to {self.data_refiner.coordinate_marker_1_label}.")
#         else:
#             self.axis_marker_1_input_field.setText(str(self.data_refiner.coordinate_marker_1_label))
#             CustomMessageBox.warning(self.parent, "Warning", """Invalid input. Please enter an "Marker + integer (ex. Marker1)".""")
            
#     def __check_axis_marker_2_input(self, text):
#         # 입력이 Marker + 숫자 인 지 확인
#         if bool(re.match(r"^Marker\d+$", text)):
#             self.data_refiner.coordinate_marker_2_label = text
#             CustomMessageBox.information(self.parent, "Information", f"The axis marker 2 has been set to {self.data_refiner.coordinate_marker_2_label}.")
#         else:
#             self.axis_marker_2_input_field.setText(str(self.data_refiner.coordinate_marker_2_label))
#             CustomMessageBox.warning(self.parent, "Warning", """Invalid input. Please enter an "Marker + integer (ex. Marker2)".""")
            
#     def __check_axis_marker_3_input(self, text):
#         # 입력이 Marker + 숫자 인 지 확인
#         if bool(re.match(r"^Marker\d+$", text)):
#             self.data_refiner.coordinate_marker_3_label = text
#             CustomMessageBox.information(self.parent, "Information", f"The axis marker 3 has been set to {self.data_refiner.coordinate_marker_3_label}.")
#         else:
#             self.axis_marker_3_input_field.setText(str(self.data_refiner.coordinate_marker_3_label))
#             CustomMessageBox.warning(self.parent, "Warning", """Invalid input. Please enter an "Marker + integer (ex. Marker3)".""")
              
#     def __check_window_size_input(self, text):
#         # 입력이 정수인지 확인
#         if text.isdigit():
#             self.data_refiner.window_size = int(text)
#             CustomMessageBox.information(self.parent, "Information", f"The window size of the filter has been set to {self.data_refiner.window_size}.")
#         else:
#             self.window_size_input_field.setText(str(self.data_refiner.window_size))
#             CustomMessageBox.warning(self.parent, "Warning", "Invalid input. Please enter an integer.")
        
#     def refine_data(self):
#         self.data_refiner.refine_data(self.target_data_list)