from ...csv import *
from ..common import *
from .common import *

from ..trainer import Trainer
from ...pyqt.widget import (ScrollWidget, CustomLineEdit, CustomMessageBox, CustomFigureCanvas)

class TrainingWidget(QWidget):
    def __init__(self, file_directory, json_data_manager, json_data_viewer, parent=None):
        self.parent = parent
        super().__init__(self.parent)
        
        # 인스턴스 저장
        self.file_directory = file_directory
        self.json_data_manager = json_data_manager
        self.json_data_viewer = json_data_viewer
        
        # Trainer 생성
        self.trainer = Trainer(
            file_directory, 
            [self.update_training_loss_animation,
             self.update_validation_loss_animation,
             self.update_test_result,
             self.export_test_result], 
            self.parent)
        
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
        self.input_locations = None
        self.output_locations = None
        self.training_epoch = None
        self.training_learning_rate = None
        
        # 초기값 설정
        self.__set_input_locations  (self.widgets["input_locations_line_edit"]        .text())
        self.__set_output_locations (self.widgets["output_locations_line_edit"]       .text())
        self.__set_epoch            (self.widgets["training_epoch_line_edit"]         .text())
        self.__set_learning_rate    (self.widgets["training_learning_rate_line_edit"] .text())
        
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
        
        self.flag = 0
         
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
        self.__add_container_label("Dataset", 30)
        
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
        self.__add_container_label("Training parameter", 30)
        
        # dataset ui container 생성
        parameter_container_layout = self.__create_container()
        
        # training parameter 관련 ui 생성
        self.__add_widget_to_layout(parameter_container_layout, "input_locations_label",             QLabel("Input locations",                   self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "input_locations_line_edit",         CustomLineEdit(self.__set_input_locations,  self.parent), 20, "line edit", "1")
        self.__add_widget_to_layout(parameter_container_layout, "output_locations_label",            QLabel("Output locations",                  self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "output_locations_line_edit",        CustomLineEdit(self.__set_output_locations, self.parent), 20, "line edit", "12, 38, 39")
        self.__add_widget_to_layout(parameter_container_layout, "training_epoch_label",              QLabel("Training epoch",                    self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "training_epoch_line_edit",          CustomLineEdit(self.__set_epoch,            self.parent), 20, "line edit", "3000")
        self.__add_widget_to_layout(parameter_container_layout, "training_learning_rate_label",      QLabel("Training learning rate",            self.parent), 20, "label")
        self.__add_widget_to_layout(parameter_container_layout, "training_learning_rate_line_edit",  CustomLineEdit(self.__set_learning_rate,    self.parent), 20, "line edit", "0.001")
        self.__add_widget_to_layout(parameter_container_layout, "training_button",                   QPushButton("Start training",               self.parent), 20, "button")
        
        # Training 버튼 액션 연결
        self.widgets["training_button"].clicked.connect(self.__start_training)
        
        # 아래쪽 빈 공간 생성
        self.scroll_widget.add_item(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Training 진행 상황 표시할 figure widget 생성
        self.__create_figure_widget()

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
            if value_type == list:
                self.widgets[variable_name+"_line_edit"].setText(str(", ".join(value)))
            else:
                self.widgets[variable_name+"_line_edit"].setText(str(value))
        
        # 정규식에서 음의 부호는 포함되지 않음
        regex = ""
        if value_type == float:
            regex = r"^(\d+(\.\d*)?|\.\d+)$" # 실수 형식의 정규식: 정수부, 소수부
        elif value_type == int:
            regex = r"^\d+$" # 정수 형식의 정규식: 정수부
        elif value_type == list:
            regex = r"^\d+(,\s*\d+)*$" # \d : 첫 번째 숫자, \s* : 0개 이상의 공백, (,\s*\d+)* : , + 공백 + 숫자 조합이 0개 이상 반복됨
            
        # 입력된 값이 정규식과 일치하는 지 확인
        if bool(re.match(regex, text)):
  
            # 주어진 type에 맞도록 text 변환
            if value_type == float:
                value = float(text)
            elif value_type == int:
                value = int(text)
            elif value_type == list:
                value = [num.strip() for num in text.split(",")]
            
            # 변경 하고자 하는 값이 현재 값과 동일한 경우 작업 종료
            if value == getattr(self, variable_name):
                return
                                
            # range가 주어진 경우
            if range is not None and value_type is not list:
                
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
            if value_type == list:
                self.widgets[variable_name+"_line_edit"].setText(str(", ".join(getattr(self, variable_name))))
            else:
                self.widgets[variable_name+"_line_edit"].setText(str(getattr(self, variable_name)))
    
    def __set_input_locations(self, text):
        self.__check_text_input_validity(text, list, "input_locations")
        
    def __set_output_locations(self, text):
        self.__check_text_input_validity(text, list, "output_locations")
        
    def __set_epoch(self, text):
        self.__check_text_input_validity(text, int, "training_epoch")
        
    def __set_learning_rate(self, text):
        self.__check_text_input_validity(text, float, "training_learning_rate")
    
    def __start_training(self):
        self.clear_canvas()
        
        target_file_data = self.json_data_manager.file_data
        
        self.trainer.set_dataset(self.__create_dataset(target_file_data, self.training_input_dataset_name_list), "training", "input")
        self.trainer.set_dataset(self.__create_dataset(target_file_data, self.training_output_dataset_name_list), "training", "output")
        self.trainer.set_dataset(self.__create_dataset(target_file_data, self.validation_input_dataset_name_list), "validation", "input")
        self.trainer.set_dataset(self.__create_dataset(target_file_data, self.validation_output_dataset_name_list), "validation", "output")
        self.trainer.set_dataset(self.__create_dataset(target_file_data, self.test_input_dataset_name_list), "test", "input")
        self.trainer.set_dataset(self.__create_dataset(target_file_data, self.test_output_dataset_name_list), "test", "output")
        
        self.trainer.start_training(
            self.input_locations,
            self.output_locations,
            self.training_epoch,
            self.training_learning_rate
        )
        
    def __create_figure_widget(self):
        """다른 위젯에 배치할 figure_widget 위젯 생성"""
        # Figure widget 생성
        self.figure_widget = QWidget()
        figure_layout = QVBoxLayout()
        self.figure_widget.setLayout(figure_layout)
        
        # Loss 표시 canvas 생성
        self.loss_plot_canvas = CustomFigureCanvas(padding=(0.05, 0.95, 0.85, 0.15), parent=self.parent)
        self.loss_plot_canvas.set_grid(1, 2)
        
        self.training_loss_ax, self.training_loss_ani_handle = self.loss_plot_canvas.get_ani_ax(0, 0, UiStyle.get_plot_color(0))
        self.validation_loss_ax, self.validation_loss_ani_handle = self.loss_plot_canvas.get_ani_ax(0, 1, UiStyle.get_plot_color(1))
        self.training_loss_ax.set_title ("Training loss", color=UiStyle.get_color("content_text_color", "fraction"))
        self.training_loss_ax.set_xlabel("Iteration",     color=UiStyle.get_color("content_text_color", "fraction"))
        self.training_loss_ax.set_ylabel("Loss",          color=UiStyle.get_color("content_text_color", "fraction"))
        
        self.validation_loss_ax.set_title ("Validation loss", color=UiStyle.get_color("content_text_color", "fraction"))
        self.validation_loss_ax.set_xlabel("Iteration",       color=UiStyle.get_color("content_text_color", "fraction"))
        self.validation_loss_ax.set_ylabel("Loss",            color=UiStyle.get_color("content_text_color", "fraction"))
        
        # Best validation loss 표시 text 생성
        best_val_layout = QVBoxLayout()
        best_val_widget = QWidget()
        best_val_widget.setLayout(best_val_layout)
        best_val_loss_label = QLabel("Best validation loss", self.parent)
        self.best_val_loss_text_field = QLabel("", self.parent)
        set_label_style(best_val_loss_label, 20)
        set_text_field_style(self.best_val_loss_text_field, 40)
        best_val_layout.addWidget(best_val_loss_label)
        best_val_layout.addWidget(self.best_val_loss_text_field)
        best_val_layout.setAlignment(best_val_loss_label, Qt.AlignCenter)
        best_val_layout.setAlignment(self.best_val_loss_text_field, Qt.AlignCenter)
        
        # Error 표시 canvas 생성
        self.result_plot_canvas = CustomFigureCanvas(padding=(0.05, 0.95, 0.85, 0.15), parent=self.parent)
        self.result_plot_canvas.set_grid(1, 3)
        
        self.shoulder_ax = self.result_plot_canvas.get_ax(0, 0)
        self.elbow_ax = self.result_plot_canvas.get_ax(0, 1)
        self.wrist_ax = self.result_plot_canvas.get_ax(0, 2)
        
        self.shoulder_ax.set_title ("Shoulder joint", color=UiStyle.get_color("content_text_color", "fraction"))
        self.shoulder_ax.set_xlabel("Time (s)",       color=UiStyle.get_color("content_text_color", "fraction"))
        self.shoulder_ax.set_ylabel("Position (mm)",  color=UiStyle.get_color("content_text_color", "fraction"))
        
        self.elbow_ax.set_title ("Elbow joint",   color=UiStyle.get_color("content_text_color", "fraction"))
        self.elbow_ax.set_xlabel("Time (s)",      color=UiStyle.get_color("content_text_color", "fraction"))
        self.elbow_ax.set_ylabel("Position (mm)", color=UiStyle.get_color("content_text_color", "fraction"))
        
        self.wrist_ax.set_title ("Wrist joint",   color=UiStyle.get_color("content_text_color", "fraction"))
        self.wrist_ax.set_xlabel("Time (s)",      color=UiStyle.get_color("content_text_color", "fraction"))
        self.wrist_ax.set_ylabel("Position (mm)", color=UiStyle.get_color("content_text_color", "fraction"))
        
        # RNSE 표시 text 생성
        rmse_layout = QVBoxLayout()
        rmse_widget = QWidget()
        rmse_widget.setLayout(rmse_layout)
        rmse_label = QLabel("RMSE", self.parent)
        self.rmse_text_field = QLabel("", self.parent)
        set_label_style(rmse_label, 20)
        set_text_field_style(self.rmse_text_field, 40)
        rmse_layout.addWidget(rmse_label)
        rmse_layout.addWidget(self.rmse_text_field)
        rmse_layout.setAlignment(rmse_label, Qt.AlignCenter)
        rmse_layout.setAlignment(self.rmse_text_field, Qt.AlignCenter)

        # 레이아웃 추가
        figure_layout.addWidget(self.loss_plot_canvas, 4)
        figure_layout.addWidget(best_val_widget, 1)
        figure_layout.addWidget(self.result_plot_canvas, 8)
        figure_layout.addWidget(rmse_widget, 1)
        
        # Canvas clear
        self.clear_canvas()

    def get_figure_widget(self):
        """figure_widget 반환"""
        self.__create_figure_widget()
        
        return self.figure_widget
    
    def clear_canvas(self):
        self.training_loss_ani_handle.clear()
        self.validation_loss_ani_handle.clear()
        self.rmse_text_field.setText("0.0000")
        self.best_val_loss_text_field.setText("0.0000")
        
        self.result_plot_canvas.clear()
        self.shoulder_ax = self.result_plot_canvas.get_ax(0, 0)
        self.elbow_ax = self.result_plot_canvas.get_ax(0, 1)
        self.wrist_ax = self.result_plot_canvas.get_ax(0, 2)
        
        self.shoulder_ax.set_title ("Shoulder joint", color=UiStyle.get_color("content_text_color", "fraction"))
        self.shoulder_ax.set_xlabel("Time (s)",       color=UiStyle.get_color("content_text_color", "fraction"))
        self.shoulder_ax.set_ylabel("Position (mm)",  color=UiStyle.get_color("content_text_color", "fraction"))
        
        self.elbow_ax.set_title ("Elbow joint",   color=UiStyle.get_color("content_text_color", "fraction"))
        self.elbow_ax.set_xlabel("Time (s)",      color=UiStyle.get_color("content_text_color", "fraction"))
        self.elbow_ax.set_ylabel("Position (mm)", color=UiStyle.get_color("content_text_color", "fraction"))
        
        self.wrist_ax.set_title ("Wrist joint",   color=UiStyle.get_color("content_text_color", "fraction"))
        self.wrist_ax.set_xlabel("Time (s)",      color=UiStyle.get_color("content_text_color", "fraction"))
        self.wrist_ax.set_ylabel("Position (mm)", color=UiStyle.get_color("content_text_color", "fraction"))
        
        self.result_plot_canvas.draw()
        
    def update_training_loss_animation(self, training_loss):
        self.training_loss_ani_handle.add_plot(training_loss)
        
    def update_validation_loss_animation(self, validation_loss):
        self.validation_loss_ani_handle.add_plot(validation_loss)
        self.best_val_loss_text_field.setText("{:.4f}".format(validation_loss))
    
    def update_test_result(self, time_label, test_estimated, test_reference, rmse):
        # Shoulder, elbow, wrist 추정 결과 plot
        self.shoulder_ax.plot(time_label[:, 0], test_estimated[:, 0], color=UiStyle.get_plot_color(0), linestyle=':')
        self.shoulder_ax.plot(time_label[:, 0], test_reference[:, 0], color=UiStyle.get_plot_color(0))
        self.shoulder_ax.plot(time_label[:, 0], test_estimated[:, 1], color=UiStyle.get_plot_color(1), linestyle=':')
        self.shoulder_ax.plot(time_label[:, 0], test_reference[:, 1], color=UiStyle.get_plot_color(1))
        self.shoulder_ax.plot(time_label[:, 0], test_estimated[:, 2], color=UiStyle.get_plot_color(2), linestyle=':')
        self.shoulder_ax.plot(time_label[:, 0], test_reference[:, 2], color=UiStyle.get_plot_color(2))
        
        self.elbow_ax.plot(time_label[:, 0], test_estimated[:, 3], color=UiStyle.get_plot_color(3), linestyle=':')
        self.elbow_ax.plot(time_label[:, 0], test_reference[:, 3], color=UiStyle.get_plot_color(3))
        self.elbow_ax.plot(time_label[:, 0], test_estimated[:, 4], color=UiStyle.get_plot_color(4), linestyle=':')
        self.elbow_ax.plot(time_label[:, 0], test_reference[:, 4], color=UiStyle.get_plot_color(4))
        self.elbow_ax.plot(time_label[:, 0], test_estimated[:, 5], color=UiStyle.get_plot_color(5), linestyle=':')
        self.elbow_ax.plot(time_label[:, 0], test_reference[:, 5], color=UiStyle.get_plot_color(5))
        
        self.wrist_ax.plot(time_label[:, 0], test_estimated[:, 6], color=UiStyle.get_plot_color(6), linestyle=':')
        self.wrist_ax.plot(time_label[:, 0], test_reference[:, 6], color=UiStyle.get_plot_color(6))
        self.wrist_ax.plot(time_label[:, 0], test_estimated[:, 7], color=UiStyle.get_plot_color(7), linestyle=':')
        self.wrist_ax.plot(time_label[:, 0], test_reference[:, 7], color=UiStyle.get_plot_color(7))
        self.wrist_ax.plot(time_label[:, 0], test_estimated[:, 8], color=UiStyle.get_plot_color(8), linestyle=':')
        self.wrist_ax.plot(time_label[:, 0], test_reference[:, 8], color=UiStyle.get_plot_color(8))
        self.result_plot_canvas.draw()
        
        # RMSE text 표시
        self.rmse_text_field.setText("{:.4f}".format(rmse))
        
    def export_test_result(self, epoch, learning_rate, iteration, execution_time, input_locations, output_locations, rmse, test_estimated, test_reference, time_label):
        # Test 결과 csv로 저장
        
        # CSV 파일 저장 경로 선택
        directory_path = QFileDialog.getExistingDirectory(self.parent, "Select Directory", "", QFileDialog.ShowDirsOnly)
        
        # 현재 시간 가져오기
        current_time = datetime.now()
        
        # 연-월-일-시-분-초 형식으로 포맷팅
        formatted_time = current_time.strftime("%Y-%m-%d-%H-%M-%S")
        
        # CSV 파일 생성
        with open(os.path.join(directory_path, "Test_result_"+formatted_time+".csv"), mode='w', newline='') as file:
            writer = csv.writer(file)

            # Training 설정 작성
            writer.writerow([" "] + ["Set epoch / learning rate"] + [epoch] + [learning_rate])
            
            # 빈 행 추가
            writer.writerow([])
            
            # Iteration 작성
            writer.writerow([" "] + ["Iteration"] + [iteration])
            
            # Execution time 작성
            writer.writerow([" "] + ["Execution time"] + [execution_time])
            
            # 빈 행 추가
            writer.writerow([])
            
            # RMSE 작성
            writer.writerow([" "] + ["RMSE (mm)"] + [rmse])
            
            # 빈 행 추가
            writer.writerow([])
            
            # Input location, output location 작성
            writer.writerow([" "] + ["Input locations"] + input_locations)
            writer.writerow([" "] + ["Output locations"] + output_locations)
            
            # 빈 행 추가
            writer.writerow([])
            
            # Estimation, reference 위치 표시
            writer.writerow([" "] + [" "] + ["Estimated data"] + [" "] * test_estimated.shape[1] + ["Reference data"])
            
            # Data column label 표시
            writer.writerow([" "] + ["Time (s)"] + output_locations + [" "] + output_locations)
            
            # time_label + estimated_data 합친 데이터 생성
            estimated_data_with_time_label = np.hstack((time_label, test_estimated))
            
            # 행 크기 확인
            num_rows = estimated_data_with_time_label.shape[0]

            # 동일한 행 크기와 열 크기가 1인 공백 배열 생성
            empty_array = np.full((num_rows, 1), " ", dtype=object)
            
            # time_label + estimated_data + reference_data 합친 데이터 생성
            estimated_data_with_blank = np.hstack((estimated_data_with_time_label, empty_array))
            full_data = np.hstack((estimated_data_with_blank, test_reference))
            
            # DataFrame 행 데이터에 첫 열에 공백 추가
            rows_with_blank = [[" "] + list(row) for row in full_data]

            # DataFrame의 내용을 작성
            writer.writerows(rows_with_blank)