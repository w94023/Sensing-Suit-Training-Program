from ..common import *
from .common import *
from .refiner import Refiner
from .splitter import Splitter
from .wireframe import WireframeStrainCalculator
               
class DataEditWidget(QWidget):
    def __init__(self, json_data_manager, json_data_viewer, json_data_plotter, parent=None):
        super().__init__(parent)
        # 인스턴스 저장
        self.parent= parent
        
        # Data refininer 생성
        self.refiner_widget_manager = Refiner(json_data_manager, json_data_viewer, self.parent)
        
        # Data splitter 생성
        self.splitter_widget_manager = Splitter(json_data_manager, json_data_viewer, json_data_plotter, self.parent)
        
        # Wireframe Strain Calculator 생성
        self.wireframe_strain_calculator = WireframeStrainCalculator(json_data_manager, json_data_viewer, self.parent)
        
        # UI 초기화
        self.__init_ui()
            
    def __init_ui(self):
        # 스크롤 영역 생성
        self.scroll_widget = ScrollWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_widget)
        self.setLayout(layout)
        
        # refiner widget dropdown widget으로 레이아웃에 추가
        refiner_dropdown_widget = DropdownWidget("Data refining", self.parent)
        refiner_widgets = self.refiner_widget_manager.init_ui()
        for widget in refiner_widgets:
            refiner_dropdown_widget.add_widget(widget)
        # container_layout.addWidget(refiner_dropdown_widget)
        self.scroll_widget.add_widget(refiner_dropdown_widget)
            
        # data split widget dropdown widget으로 레이아웃에 추가
        splitter_dropdown_widget = DropdownWidget("Data split", self.parent)
        splitter_widgets = self.splitter_widget_manager.init_ui()
        for widget in splitter_widgets:
            splitter_dropdown_widget.add_widget(widget)
        # container_layout.addWidget(splitter_dropdown_widget)
        self.scroll_widget.add_widget(splitter_dropdown_widget)
            
        # wireframe calculator dropdown widget으로 widget 레이아웃에 추가
        calculator_dropdown_widget = DropdownWidget("Wireframe calculation", self.parent)
        calculator_widget = self.wireframe_strain_calculator.init_ui()
        for widget in calculator_widget:
            calculator_dropdown_widget.add_widget(widget)
        # container_layout.addWidget(calculator_dropdown_widget)
        self.scroll_widget.add_widget(calculator_dropdown_widget)
        
        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # container_layout.addItem(spacer)
        self.scroll_widget.add_item(spacer)
        
        # self.setWidget(container_widget)
        self.setStyleSheet(f"""
                            QWidget {{
                                margin: 0px;
                                padding: 0px;
                                background-color: {PyQtAddon.get_color("background_color")};
                                }}""") 