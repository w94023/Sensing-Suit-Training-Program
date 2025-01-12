from ....pyqt_base import *
from ....ui_common import *

class CustomTitleBar(QWidget):
    def __init__(self, title, dock_widget=None, toggle_action=None):
        super().__init__()
        self.dock_widget = dock_widget
        self.toggle_action = toggle_action  # Menu에서 사용되는 토글 액션 참조

        # 타이틀바 레이아웃 설정
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(0)
        
        # 타이틀 텍스트 설정
        title_label = QLabel()
        title_label.setStyleSheet(f"""
                                  QLabel {{
                                      background-color: {PyQtAddon.get_color("title_bar_color")};
                                      color: {PyQtAddon.get_color("title_text_color")};
                                      padding-left:5px;
                                      padding-right:5px;
                                      padding-top:1px;
                                      padding-bottom:1px;
                                  }}
                                  """)
        title_label.setText(title)
        layout.addWidget(title_label)

        spacer = QSpacerItem(20, 0, QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addItem(spacer)

        # 최소화 버튼
        minimize_button = QPushButton()
        minimize_button.setFixedSize(16, 16)
        minimize_button.clicked.connect(self.minimize_window)
        PyQtAddon.set_button_icon(minimize_button, "minimize_icon.png", 16, 16)
        minimize_button.setStyleSheet(f"""
                                      QPushButton {{
                                          background-color: transparent;  /* 배경색 없음 */
                                          border: none;  /* 테두리 없음 */
                                          }}
                                      QPushButton:hover {{
                                          background-color: {PyQtAddon.get_color("minimize_button_hover_color")}
                                      }}
                                      """)
        layout.addWidget(minimize_button)

        # 닫기 버튼
        close_button = QPushButton()
        close_button.setFixedSize(16, 16)
        close_button.clicked.connect(self.close_window)
        PyQtAddon.set_button_icon(close_button, "close_icon.png", 16, 16)
        close_button.setStyleSheet(f"""
                                   QPushButton {{
                                       background-color: transparent;  /* 배경색 없음 */
                                       border: none;  /* 테두리 없음 */
                                   }}
                                   QPushButton:hover {{
                                       background-color: {PyQtAddon.get_color("close_button_hover_color")}
                                   }}
                                   """)
        layout.addWidget(close_button)

        # # 타이틀바의 스타일 설정
        self.setStyleSheet(f"""
                           background-color: {PyQtAddon.get_color("background_color")};
                           color: white;
                           font-family: {PyQtAddon.text_font};
                           """)

    def minimize_window(self):
        if self.dock_widget:
            self.dock_widget.setFloating(False)  # 도킹된 상태로 최소화

    def close_window(self):
        if self.dock_widget:
            self.dock_widget.close()  # 도킹 창 닫기
            if self.toggle_action:
                self.toggle_action.setChecked(False)  # Menu 상태도 반영
                
class CustomDockWidget(QDockWidget):
    class CustomTitleBar(QWidget):
        def __init__(self, title, dock_widget=None, toggle_action=None):
            super().__init__()
            self.dock_widget = dock_widget
            self.toggle_action = toggle_action  # Menu에서 사용되는 토글 액션 참조

            # 타이틀바 레이아웃 설정
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 5, 0, 5)
            layout.setSpacing(0)
            
            # 타이틀 텍스트 설정
            title_label = QLabel()
            title_label.setStyleSheet(f"""
                                    QLabel {{
                                        background-color: {PyQtAddon.get_color("title_bar_color")};
                                        color: {PyQtAddon.get_color("title_text_color")};
                                        padding-left:5px;
                                        padding-right:5px;
                                        padding-top:1px;
                                        padding-bottom:1px;
                                    }}
                                    """)
            title_label.setText(title)
            layout.addWidget(title_label)

            spacer = QSpacerItem(20, 0, QSizePolicy.Preferred, QSizePolicy.Minimum)
            layout.addItem(spacer)

            # 최소화 버튼
            minimize_button = QPushButton()
            minimize_button.setFixedSize(16, 16)
            minimize_button.clicked.connect(self.minimize_window)
            PyQtAddon.set_button_icon(minimize_button, "minimize_icon.png", 16, 16)
            minimize_button.setStyleSheet(f"""
                                        QPushButton {{
                                            background-color: transparent;  /* 배경색 없음 */
                                            border: none;  /* 테두리 없음 */
                                            }}
                                        QPushButton:hover {{
                                            background-color: {PyQtAddon.get_color("minimize_button_hover_color")}
                                        }}
                                        """)
            layout.addWidget(minimize_button)

            # 닫기 버튼
            close_button = QPushButton()
            close_button.setFixedSize(16, 16)
            close_button.clicked.connect(self.close_window)
            PyQtAddon.set_button_icon(close_button, "close_icon.png", 16, 16)
            close_button.setStyleSheet(f"""
                                    QPushButton {{
                                        background-color: transparent;  /* 배경색 없음 */
                                        border: none;  /* 테두리 없음 */
                                    }}
                                    QPushButton:hover {{
                                        background-color: {PyQtAddon.get_color("close_button_hover_color")}
                                    }}
                                    """)
            layout.addWidget(close_button)

            # # 타이틀바의 스타일 설정
            self.setStyleSheet(f"""
                            background-color: {PyQtAddon.get_color("background_color")};
                            color: white;
                            font-family: {PyQtAddon.text_font};
                            """)

        def minimize_window(self):
            if self.dock_widget:
                self.dock_widget.setFloating(False)  # 도킹된 상태로 최소화

        def close_window(self):
            if self.dock_widget:
                self.dock_widget.close()  # 도킹 창 닫기
                if self.toggle_action:
                    self.toggle_action.setChecked(False)  # Menu 상태도 반영
                
    def __init__(self, title, parent=None, set_floating=False):
        super().__init__(title, parent)

        # Toggle action 생성
        self.toggle_action = QAction(title, self)
        self.toggle_action.setCheckable(True)
        self.toggle_action.setChecked(True)  # 기본적으로 체크됨 (Dock 표시 중)
        self.toggle_action.triggered.connect(self.__toggle_dock_widget)

        # Title bar 배치
        self.custom_title_bar = self.CustomTitleBar(title, dock_widget=self, toggle_action=self.toggle_action)
        self.setTitleBarWidget(self.custom_title_bar)

        # False : 도킹된 상태로 시작
        self.setFloating(set_floating)  
        
        # 분리 및 도킹 시 호출되는 함수 연결
        self.topLevelChanged.connect(self.__on_dock_widget_top_level_changed)

    def __on_dock_widget_top_level_changed(self, topLevel):
        """QDockWidget이 분리되거나 다시 도킹될 때 호출되는 함수"""
        if topLevel:
            # 분리된 상태에서 창의 프레임 설정
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
            self.setStyleSheet(f"""QDockWidget {{background-color:{PyQtAddon.get_color("background_color")};}}""")
            self.show()  # 스타일 적용 후 다시 표시
        else:
            # 다시 도킹 상태로 돌아올 때
            self.show()  # 스타일 적용 후 다시 표시

    def __toggle_dock_widget(self):
        """도킹 위젯 표시/숨기기"""
        if self.toggle_action.isChecked():
            self.show()  # 표시
        else:
            self.hide()  # 숨기기
        