from ....pyqt_base import *
from ....ui_common import *

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