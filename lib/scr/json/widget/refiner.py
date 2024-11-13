from ..common import *
from .common import *

class Refiner():
    def __init__(self, json_data_manager, json_data_viewer, parent=None):
        # 인스턴스 저장
        self.json_data_manager = json_data_manager
        self.json_data_viewer = json_data_viewer
        self.parent = parent
        
        # JSON data 목록 클릭 이벤트 등록
        self.json_data_viewer.on_item_clicked += self.__on_target_data_changed
        
        # data refiner 생성
        self.data_refiner = DataRefiner(json_data_manager)
        
        # Target data list 저장
        self.target_data_list = []
        
    def init_ui(self):
        # Selected file counts label 표시
        selected_file_count_label = QLabel("Selected file count", self.parent)
        set_label_style(selected_file_count_label, 20)
        
        # Selected file counts text field 표시
        self.selected_file_count_text_field = QLabel("", self.parent)
        set_text_field_style(self.selected_file_count_text_field, 20)
        
        # Axis marker LineEidt label 표시
        axis_marker_input_field_label = QLabel("Axis markers", self.parent)
        set_label_style(axis_marker_input_field_label, 20)
        
        # Axis marker 1 input field 생성
        self.axis_marker_1_input_field = CustomLineEdit(self.__check_axis_marker_1_input, self.parent)
        set_custom_line_edit_style(self.axis_marker_1_input_field, 20, "Marker1")
        
        # Axis marker 2 input field 생성
        self.axis_marker_2_input_field = CustomLineEdit(self.__check_axis_marker_2_input, self.parent)
        set_custom_line_edit_style(self.axis_marker_2_input_field, 20, "Marker2")
        
        # Axis marker 3 input field 생성
        self.axis_marker_3_input_field = CustomLineEdit(self.__check_axis_marker_3_input, self.parent)
        set_custom_line_edit_style(self.axis_marker_3_input_field, 20, "Marker3")
        
        # Window size LineEidt label 표시
        window_size_input_field_label = QLabel("Window size", self.parent)
        set_label_style(window_size_input_field_label, 20)
        
        # Window size input field 생성
        self.window_size_input_field = CustomLineEdit(self.__check_window_size_input, parent=self.parent)
        set_custom_line_edit_style(self.window_size_input_field, 20, "50")
        
        # QSpacerItem: 빈 공간 생성
        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Maximum)
        
        # QPushButton: 입력된 텍스트를 출력하는 버튼
        button = QPushButton("Refine data", self.parent)
        button.clicked.connect(self.refine_data)
        set_button_style(button, 20)
        
        return [selected_file_count_label,
                self.selected_file_count_text_field,
                axis_marker_input_field_label,
                self.axis_marker_1_input_field,
                self.axis_marker_2_input_field,
                self.axis_marker_3_input_field,
                window_size_input_field_label,
                self.window_size_input_field,
                # spacer,
                button]
        
    def __clear(self):
        self.target_data_list.clear()
        self.selected_file_count_text_field.setText("")

    def __on_target_data_changed(self, selected_items):
        # selected item이 없거나, target file이 변경되었을 경우
        if selected_items is None:
            self.__clear()
            return

        if len(selected_items) == 0:
            self.__clear()
            return
        
        # selected item 저장
        self.target_data_list = selected_items
        
        # target file count 표시
        self.__set_target_file_count(len(self.target_data_list))

    def __set_target_file_count(self, target_file_count):
        # target file count 표시
        
        if target_file_count < 2:
            self.selected_file_count_text_field.setText(str(target_file_count)+" file")
        else:
            self.selected_file_count_text_field.setText(str(target_file_count)+" files")

    def __check_axis_marker_1_input(self, text):
        # 입력이 Marker + 숫자 인 지 확인
        if bool(re.match(r"^Marker\d+$", text)):
            self.data_refiner.coordinate_marker_1_label = text
            CustomMessageBox.information(self.parent, "Information", f"The axis marker 1 has been set to {self.data_refiner.coordinate_marker_1_label}.")
        else:
            self.axis_marker_1_input_field.setText(str(self.data_refiner.coordinate_marker_1_label))
            CustomMessageBox.warning(self.parent, "Warning", """Invalid input. Please enter an "Marker + integer (ex. Marker1)".""")
            
    def __check_axis_marker_2_input(self, text):
        # 입력이 Marker + 숫자 인 지 확인
        if bool(re.match(r"^Marker\d+$", text)):
            self.data_refiner.coordinate_marker_2_label = text
            CustomMessageBox.information(self.parent, "Information", f"The axis marker 2 has been set to {self.data_refiner.coordinate_marker_2_label}.")
        else:
            self.axis_marker_2_input_field.setText(str(self.data_refiner.coordinate_marker_2_label))
            CustomMessageBox.warning(self.parent, "Warning", """Invalid input. Please enter an "Marker + integer (ex. Marker2)".""")
            
    def __check_axis_marker_3_input(self, text):
        # 입력이 Marker + 숫자 인 지 확인
        if bool(re.match(r"^Marker\d+$", text)):
            self.data_refiner.coordinate_marker_3_label = text
            CustomMessageBox.information(self.parent, "Information", f"The axis marker 3 has been set to {self.data_refiner.coordinate_marker_3_label}.")
        else:
            self.axis_marker_3_input_field.setText(str(self.data_refiner.coordinate_marker_3_label))
            CustomMessageBox.warning(self.parent, "Warning", """Invalid input. Please enter an "Marker + integer (ex. Marker3)".""")
              
    def __check_window_size_input(self, text):
        # 입력이 정수인지 확인
        if text.isdigit():
            self.data_refiner.window_size = int(text)
            CustomMessageBox.information(self.parent, "Information", f"The window size of the filter has been set to {self.data_refiner.window_size}.")
        else:
            self.window_size_input_field.setText(str(self.data_refiner.window_size))
            CustomMessageBox.warning(self.parent, "Warning", "Invalid input. Please enter an integer.")
        
    def refine_data(self):
        self.data_refiner.refine_data(self.target_data_list)
