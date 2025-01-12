from ....pyqt_base import *
from ....ui_common import *

class CustomLineEdit(QLineEdit):
    def __init__(self, edit_finish_callback, parent=None):
        super().__init__(parent)
        # 기본 스타일 시트 설정
        self.set_default_style()
        
        # 수정 완료 시 호출 이벤트 등록
        self.edit_finish_callback = edit_finish_callback
        self.editingFinished.connect(self.check_text_input)
        
        # 메서드 호출을 통한 수정 시 콜백 호출되는 것을 방지
        self.is_handling_editing = False

    def set_default_style(self):
        # 기본 색상
        self.setStyleSheet(f"""
                            background-color: {PyQtAddon.get_color("background_color")};
                            color: {PyQtAddon.get_color("content_text_color")};
                            font-family: {PyQtAddon.text_font};
                            border: 1px solid {PyQtAddon.get_color("content_line_color")}
                            """)

    def set_focus_style(self):
        # 포커스가 있을 때 색상
        self.setStyleSheet(f"""
                            background-color: {PyQtAddon.get_color("background_color")};
                            color: {PyQtAddon.get_color("content_text_color")};
                            font-family: {PyQtAddon.text_font};
                            border: 1px solid {PyQtAddon.get_color("point_color_2")}
                            """)

    def focusInEvent(self, event):
        # 포커스를 얻었을 때 스타일 변경
        self.set_focus_style()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        # 포커스를 잃었을 때 기본 스타일로 변경
        self.set_default_style()
        super().focusOutEvent(event)
        
    def set_text_in_line_edit(self, text):
        # 메서드로 text 수정할 때, editingFinished invoke 되지 않도록 하는 메서드
        self.blockSignals(True)
        self.setText(text)
        self.blockSignals(False)
    
    def check_text_input(self):
        # 프로그램적으로 텍스트 설정 중일 때는 호출하지 않음
        if self.is_handling_editing:
            return
        
        # 플래그 설정
        self.is_handling_editing = True
    
        if self.edit_finish_callback is not None:
            self.edit_finish_callback(self.text())
            
        # 플래그 해제
        self.is_handling_editing = False