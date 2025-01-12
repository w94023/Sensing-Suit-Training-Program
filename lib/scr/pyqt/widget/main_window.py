from ....pyqt_base import *
from ....ui_common import *

from .dock_widget import CustomDockWidget

class CustomMainWindow(QMainWindow):
    def __init__(self, title, app):
        super().__init__()

        # close 이벤트 등록
        self.on_closed_callback_list = []
        self.on_resized = CustomEventHandler()

        # 메인 중앙 위젯 설정
        self.central_widget = QFrame(self)
        self.setCentralWidget(self.central_widget)
        
        # # 중첩 도킹을 활성화하여 두 개의 dockwidget을 세로로 나눌 수 있도록 설정
        # self.setDockNestingEnabled(True)

        # 아이콘 설정
        self.setWindowIcon(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "program_icon.svg"))))

        # 메인 윈도우 설정
        self.setWindowTitle(title)
        # 윈도우 최대 크기로 설정
        available_geometry = app.primaryScreen().availableGeometry()
        self.setGeometry(available_geometry)
        # 윈도우 스타일 설정
        self.setStyleSheet(f"""
                           QMainWindow {{
                               background-color: {PyQtAddon.get_color("background_color")};
                               font-family:{PyQtAddon.text_font};
                           }}

                           QMainWindow::separator {{
                               background-color: {PyQtAddon.get_color("line_color")};
                               width: 1px;  /* handle의 너비 (수직) */
                               height: 1px;  /* handle의 높이 (수평) */
                               border: none;
                           }}
                           QMainWindow::separator:hover {{
                               background-color: none;  /* hover 시 색상 변경 */
                           }}

                           QMenuBar {{
                               background-color: {PyQtAddon.get_color("background_color")};  /* MenuBar 배경색 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* MenuBar 텍스트 색상 */
                           }}
                           QMenuBar::item {{
                               background-color: transparent;  /* 항목의 기본 배경 투명 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* 항목 텍스트 색상 */
                           }}
                           QMenuBar::item:selected {{
                               background-color: {PyQtAddon.get_color("point_color_1")};  /* 선택된 항목의 배경색 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* 선택된 항목의 텍스트 색상 */
                           }}
                           QMenuBar::item:pressed {{
                               background-color: {PyQtAddon.get_color("point_color_1")};  /* 눌렀을 때의 배경색 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* 눌렀을 때의 텍스트 색상 */
                           }}
                           QMenu {{
                               background-color: {PyQtAddon.get_color("background_color")};  /* 드롭다운 메뉴 배경색 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* 드롭다운 메뉴 텍스트 색상 */
                               font-family: {PyQtAddon.text_font};  /* 드롭다운 메뉴 폰트 패밀리 */
                           }}
                           QMenu::item:selected {{
                               background-color: {PyQtAddon.get_color("point_color_2")};  /* 드롭다운 메뉴에서 선택된 항목의 배경색 */
                               color: {PyQtAddon.get_color("title_text_color")};  /* 드롭다운 메뉴에서 선택된 항목의 텍스트 색상 */
                           }}
                           """)
        
        # MenuBar 생성 및 Layout 메뉴 추가
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
                              QMenuBar {{
                              border-top: 1px solid {PyQtAddon.get_color("line_color")};
                              border-bottom: 1px solid {PyQtAddon.get_color("line_color")};
                              }}""")
        self.layout_menu = menubar.addMenu('Layout')
        self.view_menu = menubar.addMenu('View')
        
        # UI 업데이트를 위한 외부 참조 변수
        self.central_layout = None
        self.docking_widgets = {}
        self.menu_layouts = {}
        
    def resizeEvent(self, event):
        self.on_resized()
        super().resizeEvent(event)
        
    def register_on_closed_event(self, callback):
        self.on_closed_callback_list.append(callback)
        
    def closeEvent(self, event):
        for callback in self.on_closed_callback_list:
            if callback: callback(event)

    def set_central_layout(self, layout):
        self.central_widget.setLayout(layout)
        self.central_layout = layout
        
    def add_docking_widget(self, title, docking_direction):
        # docking widget 생성
        docking_widget = CustomDockWidget(title, parent=self)
        
        # DockWidget으로 추가
        self.addDockWidget(docking_direction, docking_widget)
        
        # 메뉴로 추가
        self.view_menu.addAction(docking_widget.toggle_action)
            
        self.docking_widgets[title] = docking_widget

    def add_layout_configuration(self, layout_name, dock_widgets_to_show, dock_widgets_locations, callback):
        # QAction 생성
        layout_action = QAction(layout_name, self)
        layout_action.triggered.connect(partial(self.layout_action, dock_widgets_to_show, dock_widgets_locations, callback))
        
        # 메뉴 바에 항목 등록
        self.layout_menu.addAction(layout_action)

        # 인스턴스 변수에 layout action 등록
        self.menu_layouts[layout_name] = layout_action

    def layout_action(self, dock_widgets_to_show, dock_widgets_locations, callback):
        for dock_widget in self.docking_widgets.values():
            # self.removeDockWidget(dock_widget)
            dock_widget.hide()

        for i, dock_widget in enumerate(dock_widgets_to_show):
            self.removeDockWidget(dock_widget)  # 기존 위치에서 제거
            self.addDockWidget(dock_widgets_locations[i], dock_widget)  # 변경된 위치로 이동
            dock_widget.show()

        if callback is not None:
            callback()

    def activate_layout(self, layout_name):
        if layout_name in self.menu_layouts.keys():
            self.menu_layouts[layout_name].trigger()