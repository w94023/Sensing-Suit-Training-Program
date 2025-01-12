from ..common import *
from .common import *

class WireframeStrainCalculator(QWidget):
    def __init__(self, json_data_manager, json_data_viewer, parent=None):
        self.parent= parent
        super().__init__(self.parent)

        self.calculaotor = Calculator()

        self.json_data_manager = json_data_manager
        self.json_data_viewer = json_data_viewer
        self.json_data_viewer.on_item_clicked += self.__on_target_data_changed
        
        # wireframe 계산을 위해 선택된 data list
        self.target_data_list = []

    def init_ui(self): 
        # Selected file counts label 표시
        selected_file_count_label = QLabel("Selected file count", self.parent)
        set_label_style(selected_file_count_label, 20)
        
        # Selected file counts text field 표시
        self.selected_file_count_text_field = QLabel("", self.parent)
        set_text_field_style(self.selected_file_count_text_field, 20)
           
        # strain 데이터 계산 버튼
        button = QPushButton("Calculate strain", self.parent)
        button.clicked.connect(self.__calculate_wireframe_strain)
        set_button_style(button, 20)
        
        # 빈 공간 생성
        # spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        return [
            selected_file_count_label,
            self.selected_file_count_text_field,
            button,
        ]
     
    def __clear(self):
        self.target_data_list.clear()
        self.selected_file_count_text_field.setText("")
        
    def __set_target_file_count(self, target_file_count):
        # target file count 표시
        
        if target_file_count < 2:
            self.selected_file_count_text_field.setText(str(target_file_count)+" file")
        else:
            self.selected_file_count_text_field.setText(str(target_file_count)+" files")
        
    def __on_target_data_changed(self, selected_items):
        # json_data_viewer 에서 데이터 리스트가 변경되었을 경우 호출되는 메서드
        
        # selected item이 없거나, target file이 변경되었을 경우 예외 처리
        if selected_items is None:
            self.__clear()
            return

        if len(selected_items) == 0:
            self.__clear()
            return
        
        # selected item을 wireframe 계산을 위해 선택된 data로 저장
        self.target_data_list.clear()
        for selected_item in selected_items:
            # list 형태의 데이터를 string으로 변환 후 저장
            # ex. ["AA", "marker", "raw"] > "AA-marker-raw"
            data_name = "-".join(selected_item)
            if "marker" in data_name and "refined" in data_name: # refined marker data만 input으로 받음
                self.target_data_list.append(data_name)
                
        # target file count 표시
        self.__set_target_file_count(len(self.target_data_list))
        
    def __get_target_data(self):
        # json_data_manager로부터, 현재 로드된 json 파일의 데이터 불러오기
        target_file_data = self.json_data_manager.file_data
        
        # json 파일의 데이터가 없을 경우 예외 처리
        if target_file_data is None:
            return
        
        # json 파일 데이터 내의 target data 불러오기
        # json 파일 데이터 : dictionary 타입 (key : data name)
        # ex. {"AA-marker-raw" : df, "FE-marker-raw" : df}
        df_list = {}
        for target_data in self.target_data_list:
            if target_data in target_file_data.keys():
                df_list[target_data] = target_file_data[target_data]
            
        return df_list
        
    def __calculate_wireframe_strain(self):
        # 유저가 UI에서 wireframe calculate 버튼을 누를 시 호출되는 메서드
        df_list = self.__get_target_data()
        
        # 선택된 파일이 없을 경우 예외 처리
        if len(df_list) == 0:
            CustomMessageBox.critical(self.parent, "Wireframe calculation error", "No file selected.")
            
        for key, df in df_list.items():
            # key를 list로 분리한 뒤, 다시 합쳐서 수정
            # ex. "AA-marker-raw" > "AA-wireframe-raw"
            # ex. "AA-marker-refined" > "AA-wireframe-refined"
            header_list = key.split('-')
            header_list[1] = "wireframe"
            modified_key = "-".join(header_list)
            
            df_output = self.calculaotor.get_wireframe_strain(df)
            self.json_data_manager.add_data_to_target_file(modified_key, df_output)
            
        