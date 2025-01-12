from ....pyqt_base import *
from ....ui_common import *

class CustomInputDialog(QInputDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # QInputDialog에 대한 스타일 시트 적용
        self.setStyleSheet(f"""
            QInputDialog {{
                background-color: {PyQtAddon.get_color("background_color")};
                border: none;
            }}
            QLabel {{
                color: {PyQtAddon.get_color("title_text_color")};
                font-family: {PyQtAddon.text_font};
                border: none;
            }}
            QLineEdit {{
                background-color: {PyQtAddon.get_color("point_color_1")};
                color: {PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border: 1px solid {PyQtAddon.get_color("line_color")};
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: {PyQtAddon.get_color("point_color_1")};
                color: {PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border-radius: 0px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {PyQtAddon.get_color("point_color_2")};
                border: none;
            }}
        """)

    @staticmethod
    def getText(parent, title, label, text=""):
        # CustomInputDialog 사용하여 텍스트 입력 다이얼로그 표시
        dialog = CustomInputDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setTextValue(text)
        dialog.setInputMode(QInputDialog.TextInput)

        # 입력된 텍스트 및 결과 반환
        if dialog.exec_() == QInputDialog.Accepted:
            return dialog.textValue(), True
        else:
            return "", False