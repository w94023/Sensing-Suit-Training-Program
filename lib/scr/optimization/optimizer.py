from .common import *

class OptimalSensorPlacementWidget(QWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(self.parent)

        # UI 초기화
        self.__init_ui()

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
            custom_line_edit.set_text_in_line_edit(default_text)

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

        # 
        selected_training_data_label = QLabel("Selected training data", self.parent)
        __set_label_style(selected_training_data_label, 20)

        # 
        self.selected_training_data_text_field = QLabel("", self.parent)
        __set_text_field_style(self.selected_training_data_text_field, 20)

        # 
        selected_validation_data_label = QLabel("Selected validation data", self.parent)
        __set_label_style(selected_validation_data_label, 20)

        # 
        self.selected_validation_data_text_field = QLabel("", self.parent)
        __set_text_field_style(self.selected_validation_data_text_field, 20)

        # 
        selected_test_data_label = QLabel("Selected test data", self.parent)
        __set_label_style(selected_test_data_label, 20)

        # 
        self.selected_test_data_text_field = QLabel("", self.parent)
        __set_text_field_style(self.selected_test_data_text_field, 20)

        # QSpacerItem: 빈 공간 생성
        spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        
        # QPushButton: 입력된 텍스트를 출력하는 버튼
        button = QPushButton("Find optimal sensor placement", self.parent)
        # button.clicked.connect(self.refine_data)
        __set_button_style(button, 20)

        # 레이아웃에 위젯 추가
        layout.addWidget(selected_training_data_label)
        layout.addWidget(self.selected_training_data_text_field)
        layout.addWidget(selected_validation_data_label)
        layout.addWidget(self.selected_validation_data_text_field)
        layout.addWidget(selected_test_data_label)
        layout.addWidget(self.selected_test_data_text_field)
        layout.addItem(spacer)
        layout.addWidget(button)

        self.setMaximumHeight(300)
        self.setStyleSheet(f"""
                            QWidget {{
                                margin: 0px;
                                padding: 0px;
                                background-color: {PyQtAddon.get_color("background_color")};
                                }}""")