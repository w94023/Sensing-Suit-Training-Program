from ..common import *
from .common import *

from ..optimizer import Optimizer

class OptimizationWidget(QWidget):
    def __init__(self, file_directory, json_data_manager, json_data_viewer, parent=None):
        self.parent = parent
        super().__init__(self.parent)
        
        # 인스턴스 저장
        self.file_directory = file_directory
        self.json_data_manager = json_data_manager
        self.json_data_viewer = json_data_viewer
        
        # Optimizer 생성
        self.optimizer = Optimizer(file_directory, self.parent)
        
        # json data 목록 클릭 이벤트 등록
        self.json_data_viewer.on_item_clicked += self.__on_target_data_changed

        # ui 초기화
        self.widgets = {}
        self.__init_ui()
        
        # dataset에 따른 target data list 저장
        self.training_input_dataset_name_list = []
        self.training_output_dataset_name_list = []
        self.validation_input_dataset_name_list = []
        self.validation_output_dataset_name_list = []
        self.test_input_dataset_name_list = []
        self.test_output_dataset_name_list = []
        
        # optimization parameters
        self.pre_training_epoch = None
        self.pre_training_learning_rate = None
        self.full_training_epoch = None
        self.full_training_learning_rate = None
        self.lambda_1 = None
        self.lambda_2 = None
        self.lambda_3 = None
        
        # 초기값 설정
        self.__set_pre_training_epoch         (self.widgets["pre_training_epoch_line_edit"]         .text())
        self.__set_pre_training_learning_rate (self.widgets["pre_training_learning_rate_line_edit"] .text())
        self.__set_full_training_epoch        (self.widgets["full_training_epoch_line_edit"]        .text())
        self.__set_full_training_learning_rate(self.widgets["full_training_learning_rate_line_edit"].text())
        self.__set_lambda_1                   (self.widgets["lambda_1_line_edit"]                   .text())
        self.__set_lambda_2                   (self.widgets["lambda_2_line_edit"]                   .text())
        self.__set_lambda_3                   (self.widgets["lambda_3_line_edit"]                   .text())
        
        ##### data 분류 기준 설정 #####
        # data name for training dataset
        self.data_name_for_training_dataset = ["AA", "FE", "ML", "CB1", "CB2", "CB3"]
        # data name for validation dataset
        self.data_name_for_validation_dataset = ["VALID"]
        # data name for test dataset
        self.data_name_for_test_dataset = ["TEST"]
        
        # input data type
        self.input_data_type = "wireframe"
        # output data type
        self.output_data_type = "marker"
        
        # target data state
        self.data_state = "refined"
        
    def __clear(self):
        self.training_input_dataset_name_list.clear()
        self.training_output_dataset_name_list.clear()
        self.validation_input_dataset_name_list.clear()
        self.validation_output_dataset_name_list.clear()
        self.test_input_dataset_name_list.clear()
        self.test_output_dataset_name_list.clear()
        
        for key, widget in self.widgets.items():
            if "text_field" in key:
                widget.setText("")
        
    def __append_text_to_text_field(self, text_field, text):
        text_in_text_field = text_field.text()
        if text_in_text_field == "":
            text_in_text_field += text
        else:
            text_in_text_field += "," + text
        text_field.setText(text_in_text_field)
              
    def __on_target_data_changed(self, selected_items):
        # selected item이 없거나, target file이 변경되었을 경우
        self.__clear()
        
        if selected_items is None:
            return

        if len(selected_items) == 0:
            return
        
        for item in selected_items:
            data_name = item[0]
            data_type = item[1]
            data_state = item[2]
            
            if data_state != self.data_state:
                continue
            
            # training dataset 분류
            if data_name in self.data_name_for_training_dataset:
                if data_type == self.input_data_type:
                    self.training_input_dataset_name_list.append(item)
                    self.__append_text_to_text_field(self.widgets["training_input_text_field"], data_name)
                elif data_type == self.output_data_type:
                    self.training_output_dataset_name_list.append(item)
                    self.__append_text_to_text_field(self.widgets["training_output_text_field"], data_name)
                    
            # validation dataset 분류
            if data_name in self.data_name_for_validation_dataset:
                if data_type == self.input_data_type:
                    self.validation_input_dataset_name_list.append(item)
                    self.__append_text_to_text_field(self.widgets["validation_input_text_field"], data_name)
                elif data_type == self.output_data_type:
                    self.validation_output_dataset_name_list.append(item)
                    self.__append_text_to_text_field(self.widgets["validation_output_text_field"], data_name)
                    
            # test dataset 분류
            if data_name in self.data_name_for_test_dataset:
                if data_type == self.input_data_type:
                    self.test_input_dataset_name_list.append(item)
                    self.__append_text_to_text_field(self.widgets["test_input_text_field"], data_name)
                elif data_type == self.output_data_type:
                    self.test_output_dataset_name_list.append(item)
                    self.__append_text_to_text_field(self.widgets["test_output_text_field"], data_name)  
        
    def __add_widget_to_layout(self, target_layout, key, widget, height, type, initial_text=""):
        if type == "label":
            set_label_style(widget, height)
        elif type == "text field":
            set_text_field_style(widget, height)
        elif type == "line edit":
            set_custom_line_edit_style(widget, height, initial_text)
        elif type == "button":
            set_button_style(widget, height)
        
        self.widgets[key] = widget
        if isinstance(target_layout, ScrollWidget):
            target_layout.add_widget(widget)
        else:
            target_layout.addWidget(widget)
        
    def __add_container_label(self, text, height):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter) # 가운데 정렬
        set_label_style(label, height)
        label.setStyleSheet(f"""
                            background-color:{UiStyle.get_color("point_color_5")};
                            color:{UiStyle.get_color("content_text_color")}
                            """)
        self.scroll_widget.add_widget(label)
        
    def __create_container(self):
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        widget.setStyleSheet(f"""border:1px solid {UiStyle.get_color("point_color_5")}""")
        self.scroll_widget.add_widget(widget)
        
        return layout

    def __init_ui(self):
        # scrollwidget 생성 후 레이아웃에 추가
        self.scroll_widget = ScrollWidget(self.parent)
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_widget)
        self.setLayout(layout)
        
        # dataset label 생성
        self.__add_container_label("Dataset", 20)
        
        # dataset ui container 생성
        dataset_widget_container_layout = self.__create_container()

        # dataset ui 추가
        self.__add_widget_to_layout(dataset_widget_container_layout, "training_input_label",         QLabel("Selected training input data",    self.parent), 20, "label")
        self.__add_widget_to_layout(dataset_widget_container_layout, "training_input_text_field",    QLabel("",                                self.parent), 40, "text field")
        self.__add_widget_to_layout(dataset_widget_container_layout, "training_output_label",        QLabel("Selected training output data",   self.parent), 20, "label")
        self.__add_widget_to_layout(dataset_widget_container_layout, "training_output_text_field",   QLabel("",                                self.parent), 40, "text field")
        self.__add_widget_to_layout(dataset_widget_container_layout, "validation_input_label",       QLabel("Selected validation input data",  self.parent), 20, "label")
        self.__add_widget_to_layout(dataset_widget_container_layout, "validation_input_text_field",  QLabel("",                                self.parent), 40, "text field")
        self.__add_widget_to_layout(dataset_widget_container_layout, "validation_output_label",      QLabel("Selected validation output data", self.parent), 20, "label")
        self.__add_widget_to_layout(dataset_widget_container_layout, "validation_output_text_field", QLabel("",                                self.parent), 40, "text field")
        self.__add_widget_to_layout(dataset_widget_container_layout, "test_input_label",             QLabel("Selected test input data",        self.parent), 20, "label")
        self.__add_widget_to_layout(dataset_widget_container_layout, "test_input_text_field",        QLabel("",                                self.parent), 40, "text field")
        self.__add_widget_to_layout(dataset_widget_container_layout, "test_output_label",            QLabel("Selected test output data",       self.parent), 20, "label")
        self.__add_widget_to_layout(dataset_widget_container_layout, "test_output_text_field",       QLabel("",                                self.parent), 40, "text field")
        
        # training parameter label 생성
        self.__add_container_label("Training parameter", 20)
        
        # dataset ui container 생성
        parameter_container_layout = self.__create_container()
        
        # training parameter 관련 ui 생성
        self.__add_widget_to_layout(parameter_container_layout, "pre_training_epoch_label",              QLabel("Pre training epoch",                           self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "pre_training_epoch_line_edit",          CustomLineEdit(self.__set_pre_training_epoch,          self.parent), 20, "line edit", "1000")
        self.__add_widget_to_layout(parameter_container_layout, "full_training_epoch_label",             QLabel("Full training epoch",                          self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "full_training_epoch_line_edit",         CustomLineEdit(self.__set_full_training_epoch,         self.parent), 20, "line edit", "1000")
        self.__add_widget_to_layout(parameter_container_layout, "pre_training_learning_rate_label",      QLabel("Pre training learning rate",                   self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "pre_training_learning_rate_line_edit",  CustomLineEdit(self.__set_pre_training_learning_rate,  self.parent), 20, "line edit", "0.001")
        self.__add_widget_to_layout(parameter_container_layout, "full_training_learning_rate_label",     QLabel("Full training learning rate",                  self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "full_training_learning_rate_line_edit", CustomLineEdit(self.__set_full_training_learning_rate, self.parent), 20, "line edit", "0.001")
        self.__add_widget_to_layout(parameter_container_layout, "lambda_1_label",                        QLabel("Stage 1 lambda",                               self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "lambda_1_line_edit",                    CustomLineEdit(self.__set_lambda_1,                    self.parent), 20, "line edit", "0.2")
        self.__add_widget_to_layout(parameter_container_layout, "lambda_2_label",                        QLabel("Stage 2 lambda",                               self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "lambda_2_line_edit",                    CustomLineEdit(self.__set_lambda_2,                    self.parent), 20, "line edit", "0.5")
        self.__add_widget_to_layout(parameter_container_layout, "lambda_3_label",                        QLabel("Stage 3 lambda",                               self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "lambda_3_line_edit",                    CustomLineEdit(self.__set_lambda_3,                    self.parent), 20, "line edit", "0.8")
        
        # optimization 버튼 추가
        self.__add_widget_to_layout(self.scroll_widget, "optimization_button", QPushButton("Optimize sensor placement", self.parent), 20, "button")
        self.widgets["optimization_button"].clicked.connect(self.__start_optimization)

        self.setStyleSheet(f"""
                            QWidget {{
                                margin: 0px;
                                padding: 0px;
                                background-color: {PyQtAddon.get_color("background_color")};
                                }}""")
    
    def __create_dataset(self, file_data, name_list):
        dataset = {}
        for data_name in name_list:
            key = '-'.join(data_name)
            if key in file_data.keys():
                dataset[key] = file_data[key]
                
        return dataset
    
    def __check_text_input_validity(self, text, value_type, variable_name, range=None):
        
        # range: 길이가 2인 list (min, max)
        
        def set_data():
            
            # 초기값 설정일 경우, message box 출력 X
            if getattr(self, variable_name) is not None:
                
                # 유저가 인식하기 편하도록 variable name에서 '_'를 제거하고 첫 문자를 대문자로 변환하여 출력
                target_variable_name = variable_name.capitalize() # 첫글자를 대문자로 변환
                target_variable_name = ' '.join(target_variable_name.split('_')) # '_'를 ' '로 변환
                CustomMessageBox.information(self.parent, "Information", f"{target_variable_name} has been set to {value}.")
                
            # target varaible value로 수정
            setattr(self, variable_name, value)
            self.widgets[variable_name+"_line_edit"].setText(str(value))
        
        # 정규식에서 음의 부호는 포함되지 않음
        regex = ""
        if value_type == float:
            regex = r"^(\d+(\.\d*)?|\.\d+)$" # 실수 형식의 정규식: 정수부, 소수부
        elif value_type == int:
            regex = r"^\d+$" # 정수 형식의 정규식: 정수부
            
        # 입력된 값이 정규식과 일치하는 지 확인
        if bool(re.match(regex, text)):
  
            # 주어진 type에 맞도록 text 변환
            if value_type == float:
                value = float(text)
            elif value_type == int:
                value = int(text)
            
            # 변경 하고자 하는 값이 현재 값과 동일한 경우 작업 종료
            if value == getattr(self, variable_name):
                return
                                
            # range가 주어진 경우
            if range is not None:
                
                # 주어진 range 내에 value가 존재할 경우
                if value >= range[0] and value <= range[1]:
                    
                    # data로 set
                    set_data()
                     
                # 주어진 range 내에 value가 존재할 경우   
                else:
                    # 주어진 range의 최대, 최소값을 넘지 않도록 수정 후 data로 set
                    value = min(range[1], value)
                    value = max(range[0], value)
                    
                    CustomMessageBox.warning(self.parent, "Warning", f"A number outside the allowed range was provided: adjusted to {value}.")
                    set_data()
                 
            # range가 주어지지 않은 경우, text로 변환된 값 바로 data로 저장
            else:
                set_data()
            
        else:
            CustomMessageBox.warning(self.parent, "Warning", f"Invalid input. Please enter an {value_type.__name__}")
            # 원래 varialble의 값으로 line edit text 복구
            self.widgets[variable_name+"_line_edit"].setText(str(getattr(self, variable_name)))
    
    def __set_pre_training_epoch(self, text):
        self.__check_text_input_validity(text, int, "pre_training_epoch")
        
    def __set_pre_training_learning_rate(self, text):
        self.__check_text_input_validity(text, float, "pre_training_learning_rate")
        
    def __set_full_training_epoch(self, text):
        self.__check_text_input_validity(text, int, "full_training_epoch")
        
    def __set_full_training_learning_rate(self, text):
        self.__check_text_input_validity(text, float, "full_training_learning_rate")
        
    def __set_lambda_1(self, text):
        self.__check_text_input_validity(text, float, "lambda_1", [0, 1])
        
    def __set_lambda_2(self, text):
        self.__check_text_input_validity(text, float, "lambda_2", [0, 1])
        
    def __set_lambda_3(self, text):
        self.__check_text_input_validity(text, float, "lambda_3", [0, 1])
    
    def __start_optimization(self):
        target_file_data = self.json_data_manager.file_data
        
        self.optimizer.set_dataset(self.__create_dataset(target_file_data, self.training_input_dataset_name_list), "training", "input")
        self.optimizer.set_dataset(self.__create_dataset(target_file_data, self.training_output_dataset_name_list), "training", "output")
        self.optimizer.set_dataset(self.__create_dataset(target_file_data, self.validation_input_dataset_name_list), "validation", "input")
        self.optimizer.set_dataset(self.__create_dataset(target_file_data, self.validation_output_dataset_name_list), "validation", "output")
        
        self.optimizer.start_optimization(
            self.pre_training_epoch,
            self.pre_training_learning_rate,
            self.full_training_epoch,
            self.full_training_learning_rate,
            self.lambda_1,
            self.lambda_2,
            self.lambda_3
        )