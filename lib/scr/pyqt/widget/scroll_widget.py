from ....pyqt_base import *
from ....ui_common import *

class ScrollWidget(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 스크롤 영역이 창 크기에 맞게 조정되도록 설정
        self.setWidgetResizable(True)  
        
        # container 레이아웃 및 위젯 생성
        self.__container_layout = QVBoxLayout()
        self.__container_widget = QWidget()
        self.__container_widget.setLayout(self.__container_layout)
        
        # layout margin 삭제
        self.__container_layout.setContentsMargins(0, 0, 0, 0)
        
        # 표시할 widget 및 stylesheet 설정
        self.setWidget(self.__container_widget)
        self.setStyleSheet(f"""
                            QWidget {{
                                margin: 0px;
                                padding: 0px;
                                background-color: {PyQtAddon.get_color("background_color")};
                                }}"""
                                +PyQtAddon.vertical_scrollbar_style
                                +PyQtAddon.horizontal_scrollbar_style) 
        
    def add_widget(self, widget):
        self.__container_layout.addWidget(widget)
        
    def add_item(self, item):
        self.__container_layout.addItem(item) 