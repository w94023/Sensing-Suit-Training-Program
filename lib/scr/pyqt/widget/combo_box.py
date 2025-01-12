from ....pyqt_base import *
from ....ui_common import *

class CustomComboBox(QComboBox):
        def __init__(self, parent=None):
            super().__init__(parent)
            
            # Dropdown 펼쳐질 때 사용할 ListView 설정
            list_view = QListView()
            list_view.setFocusPolicy(Qt.NoFocus)  # QListView에 포커스 정책 설정 (포커스 없음)
            list_view.setStyleSheet(f"""border:1px solid {PyQtAddon.get_color("line_color")};""")
            self.setView(list_view)  # QComboBox에 수정된 QListView 설정
            self.setStyleSheet(f"""
                            QComboBox {{
                                background-color: {PyQtAddon.get_color("background_color")};
                                color: {PyQtAddon.get_color("content_text_color")};
                                border: 1px solid {PyQtAddon.get_color("line_color")}
                            }}
                            QComboBox QAbstractItemView {{
                                background: {PyQtAddon.get_color("background_color")};   /* 드롭다운 목록의 전체 배경색 변경 */
                                color: {PyQtAddon.get_color("content_text_color")};           /* 항목 텍스트 색상 변경 */
                                selection-background-color: {PyQtAddon.get_color("point_color_5")}; /* 항목 선택 시 배경색 변경 */
                                selection-color: {PyQtAddon.get_color("content_text_color")};    /* 항목 선택 시 텍스트 색상 변경 */
                            }}    
                            """)
            
        # def register_on_current_index_changed_event(self, callback):
        #     self.on_current_index_changed_callback_list.append(callback)
            
        # def register_on_clicked_event(self, callback):
        #     self.on_clicked_callback_list.append(callback)
            
        # def showPopup(self):
        #     # 드롭다운 메뉴가 확장될 때 호출되는 메서드 (클릭 될 때 호출됨)
        #     # 현재 선택을 자동으로 첫 번째 항목으로 변경하지 않도록 유지
        #     do_popup = True
            
        #     for callback in self.on_clicked_callback_list:
        #         if callback: do_popup = callback()
                
        #     if do_popup is None or do_popup is True: # None : default
        #         super().showPopup()

        # def __on_current_index_changed(self):
        #     self.selected_option = self.currentText()
        #     for callback in self.on_current_index_changed_callback_list:
        #         if callback: callback(self.selected_option)