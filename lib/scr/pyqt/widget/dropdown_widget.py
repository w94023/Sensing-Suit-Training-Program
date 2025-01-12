from ....pyqt_base import *
from ....ui_common import *

class DropdownWidget(QWidget):
    def __init__(self, text=None, parent=None):
        super().__init__(parent)
        
        # 토글 버튼 생성
        self.toggle_button = QPushButton(self)
        
        # 버튼 텍스트 설정
        if text is not None:
            self.toggle_button.setText(text)        
            
        # 버튼 액션 설정
        self.toggle_button.clicked.connect(self.__toggle_dropdown)

        # 확장할 위젯 컨테이너 생성
        self.__dropdown_container = QWidget(self)
        self.__dropdown_layout = QVBoxLayout(self.__dropdown_container)
        self.__dropdown_container.setVisible(True)  # 처음에는 표시 상태로 설정
        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.__dropdown_container)
        self.setLayout(self.layout)
        
        self.disabled_button_style = f"""
                                     QPushButton {{
                                         background-color:none;
                                         color:{UiStyle.get_color("title_text_color")};
                                         border: none;
                                         padding: 5px;
                                     }}
                                     QPushButton:hover {{
                                         background-color: {PyQtAddon.get_color("point_color_5")}
                                     }}
                                     """
        self.enabled_button_color = f"""
                                    QPushButton {{
                                        background-color:{UiStyle.get_color("point_color_5")};
                                        color:{UiStyle.get_color("content_text_color")};
                                        border: none;
                                        padding: 5px;
                                    }}
                                    QPushButton:hover {{
                                        background-color: {PyQtAddon.get_color("point_color_1")}
                                    }}
                                    """
        
        # 스타일 설정
        self.toggle_button.setStyleSheet(self.enabled_button_color)
        self.__dropdown_container.setStyleSheet(f"""
                                                border:1px solid {UiStyle.get_color("point_color_5")};
                                                """)
        
    def __toggle_dropdown(self):
        """드롭다운 위젯을 표시하거나 숨김"""
        is_visible = self.__dropdown_container.isVisible()
        self.__dropdown_container.setVisible(not is_visible)
        
        if is_visible:
            self.toggle_button.setStyleSheet(self.disabled_button_style)
        else:
            self.toggle_button.setStyleSheet(self.enabled_button_color)
        
    def add_widget(self, widget):
        if isinstance(widget, QWidget):
            self.__dropdown_layout.addWidget(widget)
        elif isinstance(widget, QSpacerItem):
            self.__dropdown_layout.addItem(widget)
        else:
            self.__dropdown_layout.addLayout(widget)