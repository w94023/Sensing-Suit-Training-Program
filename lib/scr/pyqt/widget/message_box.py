from ....pyqt_base import *
from ....ui_common import *

class CustomMessageBox(QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 스타일 시트 설정 (여기서 QMessageBox에 대한 스타일을 적용)
        self.setStyleSheet(f"""
            QMessageBox {{
                background-color:{PyQtAddon.get_color("background_color")};
                border:none;
            }}
            QLabel {{
                border:none;
            }}
            QMessageBox QPushButton {{
                background-color:{PyQtAddon.get_color("point_color_1")};
                color:{PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border-radius: 0px;
                border:none;
            }}
            QMessageBox QPushButton:hover {{
                background-color:{PyQtAddon.get_color("point_color_2")};
                border:none;
            }}
        """)

    @staticmethod
    def information(parent, title, text):
        # 기본 QMessageBox.warning() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)

        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)

        # 경고 아이콘 설정
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()
    
    @staticmethod
    def question(parent, title, text, setStandardButtons, setDefaultButton):
        # 기본 QMessageBox.question() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)

        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)

        # 질문 아이콘 설정
        msg_box.setIcon(QMessageBox.Question)
        
        # Standarad 버튼 설정
        msg_box.setStandardButtons(setStandardButtons)
        
        # 기본 선택 설정
        msg_box.setDefaultButton(setDefaultButton)

        # 사용자의 응답 반환
        return msg_box.exec_()

    @staticmethod
    def warning(parent, title, text):
        # 기본 QMessageBox.warning() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)

        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)

        # 경고 아이콘 설정
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()

    @staticmethod
    def critical(parent, title, text):
        # 기본 QMessageBox.critical() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)
        
        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)
        
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()