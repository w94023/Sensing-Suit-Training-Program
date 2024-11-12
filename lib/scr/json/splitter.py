from .common import *

class LatchToggleButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        
        self.setText(text)
        self.setCheckable(True)  # 버튼을 체크 가능 상태로 설정
        self.setStyleSheet(self.__get_button_style(False))  # 초기 스타일 설정
        self.clicked.connect(self.__toggle_button_clicked)  # 클릭 시 이벤트 연결
        
        self.on_toggled = CustomEventHandler()
        
    def toggle(self):
        # checked 일 경우 unchecked, unchecked일 경우 checked로 toggle state 전환
        if self.isChecked():
            self.setStyleSheet(self.__get_button_style(False))
            self.on_toggled(False)
        else:
            self.setStyleSheet(self.__get_button_style(True))
            self.on_toggled(True)
        
    def __toggle_button_clicked(self):
        """토글 버튼 클릭 시 호출되는 메서드"""
        if self.isChecked():
            self.setStyleSheet(self.__get_button_style(True))
            self.on_toggled(True)
        else:
            self.setStyleSheet(self.__get_button_style(False))
            self.on_toggled(False)
            
    def __get_button_style(self, is_checked):
        """버튼 스타일을 반환하는 메서드"""
        if is_checked:
            return f"""
                QPushButton {{
                    background-color: {UiStyle.get_color("point_color_6")};
                    color: {UiStyle.get_color("content_text_color")};
                    padding: 4px 8px;
                    border-radius: 0px;
                    border:none;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {UiStyle.get_color("point_color_1")};
                    color: {UiStyle.get_color("content_text_color")};
                    padding: 4px 8px;
                    border-radius: 0px;
                    border:none;
                }}
            """

class DataSplittingWidget(QWidget):
    def __init__(self, json_data_manager, json_data_viewer, json_data_plotter, parent=None):
        self.parent= parent
        super().__init__(self.parent)
        
        # JSON data 관리 인스턴스 저장
        self.json_data_manager = json_data_manager
        self.json_data_viewer = json_data_viewer
        self.json_data_plotter = json_data_plotter
        
        # JSON data 목록 클릭 이벤트 등록
        self.json_data_viewer.on_item_double_clicked += self.__on_item_double_clicked
        self.target_data = None
        
        # split point show flag
        self.show_split_point = False
        self.split_point_vline = None
        
        # Output file name
        self.output_file_name_first = None
        self.output_file_name_second = None
        
        # UI 초기화
        self.__init_ui()
        
    def split_data(self):
        if self.target_data is None:
            CustomMessageBox.critical(self.parent, "Data split error", "Target JSON data is not set.")
            return
        
        if self.split_point_slider.value() < 0 or  self.split_point_slider.value() >= self.target_data.shape[0]:
            CustomMessageBox.critical(self.parent, "Data split error", "The split point is outside the range of the target JSON data.")
            return
        
        split_data = split_dataframe(self.target_data, int(self.split_point_slider.value()), axis=0)
        
        # CSV 파일 저장 경로 선택
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "", QFileDialog.ShowDirsOnly)

        # 유저가 directory를 선택하지 않았을 경우
        if not directory_path:
            CustomMessageBox.warning(self.parent, "Data split result", "The operation has been canceled.")
            return
        
        exported_file_names = ""
        
        # 첫 번째 데이터 저장
        # 중복된 파일이 존재할 경우
        if os.path.isfile(os.path.join(directory_path, self.output_file_name_first)):
            # 사용자에게 확인 메시지 띄우기
            reply = CustomMessageBox.question(
                self.parent, 
                "File save", 
                f"A duplicate file exists. Do you want to continue with the CSV file export? ({self.output_file_name_first})", 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                save_csv_file(os.path.join(directory_path, self.output_file_name_first), split_data[0])
                exported_file_names += self.output_file_name_first + ", "
                
        else:
            save_csv_file(os.path.join(directory_path, self.output_file_name_first), split_data[0])
            exported_file_names += self.output_file_name_first + ", "
            
        # 두 번째 데이터 저장
        # 중복된 파일이 존재할 경우
        if os.path.isfile(os.path.join(directory_path, self.output_file_name_second)):
            # 사용자에게 확인 메시지 띄우기
            reply = CustomMessageBox.question(
                self.parent, 
                "File save", 
                f"A duplicate file exists. Do you want to continue with the CSV file export? ({self.output_file_name_second})", 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                save_csv_file(os.path.join(directory_path, self.output_file_name_second), split_data[1])
                exported_file_names += self.output_file_name_second
                
        else:
            save_csv_file(os.path.join(directory_path, self.output_file_name_second), split_data[1])  
            exported_file_names += self.output_file_name_second    
        
        CustomMessageBox.information(self.parent, "Data split done", 
                                     f"The data split has been completed with filenames ({exported_file_names}) at the split point {self.split_point_slider.value()}.")
             
    def __clear(self):
        # 인스턴스 데이터 초기화
        self.target_data = None
        
        # 위젯 초기화
        self.selected_data_name_text_field.setText("")
        self.first_result_data_name_text_field.setText("")
        self.second_result_data_name_text_field.setText("")
        self.__set_slider_range(0, 100)
        
        # 토글 버튼 초기화
        if self.show_split_point:
            self.split_point_show_toggle_button.toggle()
            
        # Output 파일명 초기화
        self.output_file_name_first = None
        self.output_file_name_second = None
        
    def __show_split_point(self, enable):
        # Toggle 버튼의 동작에 따라 plotter에 split point 표시하는 메서드
        self.show_split_point = enable
        self.__on_split_point_changed(self.split_point_slider.value())
        
    def __on_split_point_changed(self, value):
        # json_data_plotter의 ax에 axvline을 생성해서 split point 표시하는 메서드
        if self.show_split_point:
            if self.json_data_plotter.ax is not None:
                if self.split_point_vline is not None:
                    self.split_point_vline.remove()
                    
                self.split_point_vline = self.json_data_plotter.ax.axvline(x=self.target_data.iloc[value, 0], color=UiStyle.get_color("point_color_6", "fraction"), linestyle='-', linewidth=2)
                self.json_data_plotter.canvas.draw()
                
        else:
            if self.split_point_vline is not None:
                self.split_point_vline.remove()
                self.split_point_vline = None
                self.json_data_plotter.canvas.draw()
        
    def __set_target_data(self, target_data_name):
        # target_data_name을 기반으로 UI 설정하고, split 준비하는 메서드
        if not target_data_name.endswith(".csv"):
            target_data_name += ".csv"
            
        self.selected_data_name_text_field.setText(target_data_name)
        
        # output file name (first) 설정
        self.output_file_name_first = target_data_name[:-4]+"_1.csv"
        self.first_result_data_name_text_field.setText(self.output_file_name_first)
        
        # output file name (second) 설정
        self.output_file_name_second = target_data_name[:-4]+"_2.csv"
        self.second_result_data_name_text_field.setText(self.output_file_name_second)
        
        # 현재 load된 json file data 불러오기
        json_data = self.json_data_manager.file_data
        
        # json_data 내의 target data 불러오기
        self.target_data = json_data[target_data_name[:-4]]
        
        # target_data의 길이에 따라 slider의 range 조정
        self.__set_slider_range(0, self.target_data.shape[0]-1)
        
    def __on_item_double_clicked(self, selected_data):
        if selected_data is None:
            self.__clear()
            return
                
        if len(selected_data) == 0:
            self.__clear()
            return
                
        target_data_name = "-".join(selected_data)
        self.__set_target_data(target_data_name)
        
    def __set_slider_range(self, min_value, max_value):
        self.split_point_slider.setMinimum(min_value)
        self.split_point_slider.setMaximum(max_value)
        self.split_point_slider.setValue(int((max_value-min_value)/2))
        
        # 슬라이더의 눈금을 자동으로 10개 정도 생성되게 설정
        range_value = max_value - min_value
        
        # 눈금을 약 10개로 설정
        if range_value > 0:
            tick_interval = range_value // 10  # 범위를 10개로 나눈 값 설정
            self.split_point_slider.setTickInterval(tick_interval)
        
    def __set_first_output_file_name(self, text):
        if not text.endswith(".csv"):
            text += ".csv"
            self.first_result_data_name_text_field.setText(text)
            
        self.output_file_name_first = text
        CustomMessageBox.information(self.parent, "Information", f"The first output file name has been set to {self.output_file_name_first}.")
        
    def __set_second_output_file_name(self, text):
        if not text.endswith(".csv"):
            text += ".csv"
            self.second_result_data_name_text_field.setText(text)
            
        self.output_file_name_second = text
        CustomMessageBox.information(self.parent, "Information", f"The second output file name has been set to {self.output_file_name_second}.")
        
    def __init_ui(self):
        def __set_label_style(label, height):
            label.setFixedSize(0, height)
            label.setMinimumSize(0, height)
            label.setMaximumSize(16777215, height)
            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            label.setStyleSheet(f"""
                                 background-color: {UiStyle.get_color("background_color")};
                                 color: {UiStyle.get_color("content_text_color")};
                                 font-family: {UiStyle.text_font};
                                 """)
            
        def __set_text_field_style(text_field, height):
            text_field.setFixedSize(0, height)
            text_field.setMinimumSize(0, height)
            text_field.setMaximumSize(16777215, height)
            text_field.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            text_field.setStyleSheet(f"""
                                      background-color: {PyQtAddon.get_color("background_color")};
                                      color: {PyQtAddon.get_color("content_text_color")};
                                      font-family: {PyQtAddon.text_font};
                                      border: 1px solid {PyQtAddon.get_color("content_line_color")};
                                      """)
            
        def __set_custom_line_edit_style(custom_line_edit, height, default_text):
            custom_line_edit.setFixedSize(0, height)
            custom_line_edit.setMinimumSize(0, height)
            custom_line_edit.setMaximumSize(16777215, height)
            custom_line_edit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            custom_line_edit.set_text_in_line_edit(default_text) # 기본값 설정

        def __set_button_style(button, height):
            button.setFixedSize(0, height)
            button.setMinimumSize(0, height)
            button.setMaximumSize(16777215, height)
            button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            button.setStyleSheet(f"""
                                  QPushButton {{
                                      background-color: {PyQtAddon.get_color("point_color_1")};
                                      color: {PyQtAddon.get_color("content_text_color")};
                                      padding: 4px 8px;
                                      border-radius: 0px;
                                      border: none;
                                  }}
                                  QPushButton:hover {{
                                      background-color: {PyQtAddon.get_color("point_color_5")};
                                      border: none;
                                  }}
                                  """)
            
        # 레이아웃 생성
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # target data name label 표시
        selected_data_name_label = QLabel("Target data name", self.parent)
        __set_label_style(selected_data_name_label, 20)
        
        # target data name text field 표시
        self.selected_data_name_text_field = QLabel("", self.parent)
        __set_text_field_style(self.selected_data_name_text_field, 20)
        
        # first result data name label 표시
        first_result_data_name_label = QLabel("Result data name (first)", self.parent)
        __set_label_style(first_result_data_name_label, 20)
        
        # first result data name text field 생성
        self.first_result_data_name_text_field = CustomLineEdit(self.__set_first_output_file_name, self.parent)
        __set_custom_line_edit_style(self.first_result_data_name_text_field, 20, "")
        
        # second result data name label 표시
        second_result_data_name_label = QLabel("Result data name (second)", self.parent)
        __set_label_style(second_result_data_name_label, 20)
        
        # second result data name text field 생성
        self.second_result_data_name_text_field = CustomLineEdit(self.__set_second_output_file_name, self.parent)
        __set_custom_line_edit_style(self.second_result_data_name_text_field, 20, "")
        
        # split point label 생성
        split_point_label = QLabel("Split point", self.parent)
        __set_label_style(split_point_label, 20)
        
        # 슬라이더 설정
        self.split_point_slider = QSlider(Qt.Horizontal)
        self.split_point_slider.setTickInterval(1)  # 슬라이더의 표시 간격을 1로 설정
        self.split_point_slider.setSingleStep(1)    # 한 번 움직일 때마다 1만큼 이동하도록 설정
        self.split_point_slider.setTickPosition(QSlider.TicksBelow)  # 슬라이더 아래에 눈금 표시
        self.split_point_slider.valueChanged.connect(self.__on_split_point_changed)
        self.__set_slider_range(0, 50) # 초기값 설정
        
        # QSpacerItem: 빈 공간 생성
        spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        
        # split point show 토글 버튼 생성 및 설정
        self.split_point_show_toggle_button = LatchToggleButton("Show split point")
        self.split_point_show_toggle_button.on_toggled += self.__show_split_point
        
        # data split 버튼 생성
        button = QPushButton("Split data", self.parent)
        button.clicked.connect(self.split_data)
        __set_button_style(button, 20)
        
        layout.addWidget(selected_data_name_label)
        layout.addWidget(self.selected_data_name_text_field)
        layout.addWidget(first_result_data_name_label)
        layout.addWidget(self.first_result_data_name_text_field)
        layout.addWidget(second_result_data_name_label)
        layout.addWidget(self.second_result_data_name_text_field)
        layout.addWidget(split_point_label)
        layout.addWidget(self.split_point_slider)
        layout.addItem(spacer)
        layout.addWidget(self.split_point_show_toggle_button)
        layout.addWidget(button)
        
        self.setMaximumHeight(300)
        self.setStyleSheet(f"""
                            QWidget {{
                                margin: 0px;
                                padding: 0px;
                                background-color: {PyQtAddon.get_color("background_color")};
                                }}""")