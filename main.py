from lib.base import *
from lib.pyqt_base import *

from lib.scr.pyqt import *
from lib.scr.pyqt.widget import *
from lib.scr.preparation import *
from lib.scr.preparation.widget import *
from lib.scr.data import *
from lib.scr.optimization import *
from lib.scr.optimization.widget import *
from lib.scr.training import *
from lib.scr.training.widget import *

class AppManager():
    def __init__(self, target_directory):
        # 화면 설정
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        # Application 생성
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        
        # Initial 디렉토리 저장
        self.target_directory = target_directory
        # preparation data 디렉토리
        self.preparation_data_directory = os.path.join(current_file_path, "data")
        # optimization result 디렉토리
        self.optimization_result_directory = os.path.join(current_file_path, "optimization")
        
        # Main window 생성 및 최대화
        self.ui_window = CustomMainWindow("Sensor demo program", app)
        self.ui_window.showMaximized()
        
        # UI 생성
        self.create_ui()
        
        # Main window 종료 시 호출 이벤트 연결
        app.aboutToQuit.connect(self.on_app_exit)
        
        # Main window이 바로 닫히지 않고 user input을 대기하도록 설정
        sys.exit(app.exec_())
        
    def create_ui(self):
        # Central layout 생성
        self.ui_window.set_central_layout(QVBoxLayout())
        
        # Docking layout 생성
        self.ui_window.add_docking_widget("Directory",             Qt.LeftDockWidgetArea)
        self.ui_window.add_docking_widget("Data",                  Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Data viewer",           Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Labels",                Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Data edit",             Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Optimization",          Qt.RightDockWidgetArea)
        # self.ui_window.add_docking_widget("Optimized data",        Qt.RightDockWidgetArea)
        # self.ui_window.add_docking_widget("Optimized data viewer", Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Training",              Qt.RightDockWidgetArea)
        
        self.ui_window.docking_widgets["Data"].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)  # 레이아웃 정책 설정
        self.ui_window.docking_widgets["Data viewer"].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)  # 레이아웃 정책 설정

        # File tree viewer + file browser 생성 후 layout에 배치
        file_viewer = CustomFileSystemWidget(self.target_directory)
        self.ui_window.docking_widgets["Directory"].setWidget(file_viewer)
        
        #############################################
        #          Preparation widget 생성          #
        #############################################
        # data handler 생성
        preparation_data_handler = DataHandler(self.preparation_data_directory, '.h5', 3, '-')

        # JSON 뷰어 배치
        preparation_data_list_viewer = PreparationDataListViewer(preparation_data_handler, self.preparation_data_directory, parent=self.ui_window)
        self.ui_window.docking_widgets["Data"].setWidget(preparation_data_list_viewer)

        # JSON data 뷰어 배치
        preparation_data_viewer = PreparationDataViewer(preparation_data_handler, parent=self.ui_window)
        self.ui_window.docking_widgets["Data viewer"].setWidget(preparation_data_viewer)

        # JSON Data plot widget 생성 및 배치
        json_data_plotter = PreparationDataPlotter(preparation_data_handler, preparation_data_viewer, parent=self.ui_window)
        self.json_data_plot_canvas = json_data_plotter.get_figure_widget()
        self.ui_window.docking_widgets["Labels"].setWidget(json_data_plotter)
        
        # data refining widget 배치
        data_edit_widget = PreparationDataEditWidget(preparation_data_handler, preparation_data_viewer, json_data_plotter, parent=self.ui_window)
        self.ui_window.docking_widgets["Data edit"].setWidget(data_edit_widget)

        #########################################################
        #                Optimization widgets                   #
        #########################################################
        
        # optimization_data_handler = DataHandler(self.optimization_result_directory, '.h5', 3, '-')

        optimizer_widget = OptimizationWidget(self.optimization_result_directory, preparation_data_handler, preparation_data_viewer, parent=self.ui_window)
        self.optimization_plot_canvas = optimizer_widget.get_figure_widget()
        self.ui_window.docking_widgets["Optimization"].setWidget(optimizer_widget)

        # optimization_result_list_viewer = OptimizationResultDataListViewer(optimization_data_handler, self.optimization_result_directory, parent=self.ui_window)
        # self.ui_window.docking_widgets["Optimized data"].setWidget(optimization_result_list_viewer)
        
        # optimization_result_data_viewer = OptimizationResultDataViewer(optimization_data_handler, parent=self.ui_window)
        # self.ui_window.docking_widgets["Optimized data viewer"].setWidget(optimization_result_data_viewer)
        
        # self.ui_window.central_layout.addWidget(self.optimization_plot_canvas)
        
        #########################################################
        #                   Training widgets                    #
        #########################################################
        
        training_widget = TrainingWidget(self.optimization_result_directory, preparation_data_handler, preparation_data_viewer, parent=self.ui_window)
        self.training_plot_canvas = training_widget.get_figure_widget()
        self.ui_window.docking_widgets["Training"].setWidget(training_widget)
        
        #########################################################
        #                  Layout configuration                 #
        #########################################################

        preparation_layout_action = QAction("Preparation", self.ui_window)
        preparation_layout_action.triggered.connect(self.__set_preparation_layout)
        self.ui_window.layout_menu.addAction(preparation_layout_action)
        
        optimization_layout_action = QAction("Optimization", self.ui_window)
        optimization_layout_action.triggered.connect(self.__set_optimization_layout)
        self.ui_window.layout_menu.addAction(optimization_layout_action)
        
        training_layout_action = QAction("Training", self.ui_window)
        training_layout_action.triggered.connect(self.__set_training_layout)
        self.ui_window.layout_menu.addAction(training_layout_action)
        
        preparation_layout_action.trigger()
        
        self.ui_window.on_resized += self.__update_dock_widget_minimum_sizes
        
    def __update_dock_widget_minimum_sizes(self):
        # QMainWindow 크기의 10%로 Dock Widget의 최소 크기 설정
        main_window_width = self.ui_window.width()
        dock_min_width = int(main_window_width * 0.1)
        
        # 최소 크기 설정
        for dock_widget in self.ui_window.docking_widgets.values():
            dock_widget.setMinimumWidth(dock_min_width)
        
    def __set_preparation_layout(self):
        widget_name_list = ["Directory", "Data", "Data viewer", "Labels", "Data edit"]
        target_location = [Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea, Qt.RightDockWidgetArea, Qt.RightDockWidgetArea, Qt.RightDockWidgetArea]
        for dock_widget in self.ui_window.docking_widgets.values():
            self.ui_window.removeDockWidget(dock_widget)
            dock_widget.hide()

        for i, widget_name in enumerate(widget_name_list):
            self.ui_window.addDockWidget(target_location[i], self.ui_window.docking_widgets[widget_name])  # 변경된 위치로 이동
            self.ui_window.docking_widgets[widget_name].show()

        self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Labels"], Qt.Horizontal)
        self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Labels"], self.ui_window.docking_widgets["Data edit"], Qt.Horizontal)
        self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"], Qt.Vertical)
        self.ui_window.resizeDocks(
            [self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"]], 
            [1, 1],
            Qt.Vertical
        )
        
        # Clear central layout
        PyQtAddon.clear_layout(self.ui_window.central_layout)
        
        # Central layout에 json_data_plot_canvas 배치
        self.ui_window.central_layout.addWidget(self.json_data_plot_canvas)
        
    def __set_optimization_layout(self):
        widget_name_list = ["Data", "Data viewer", "Optimization"]
        target_location = [Qt.LeftDockWidgetArea, Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea]
        for dock_widget in self.ui_window.docking_widgets.values():
            self.ui_window.removeDockWidget(dock_widget)
            dock_widget.hide()

        for i, widget_name in enumerate(widget_name_list):
            self.ui_window.addDockWidget(target_location[i], self.ui_window.docking_widgets[widget_name])  # 변경된 위치로 이동
            self.ui_window.docking_widgets[widget_name].show()

        self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"], Qt.Vertical)
        self.ui_window.resizeDocks(
            [self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"]], 
            [1, 1],
            Qt.Vertical
        )
        
        # Clear central layout
        PyQtAddon.clear_layout(self.ui_window.central_layout)
        
        # Central layout에 optimization_plot_canvas 배치
        self.ui_window.central_layout.addWidget(self.optimization_plot_canvas)
        
    def __set_training_layout(self):
        widget_name_list = ["Data", "Data viewer", "Training"]
        target_location = [Qt.LeftDockWidgetArea, Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea]
        for dock_widget in self.ui_window.docking_widgets.values():
            self.ui_window.removeDockWidget(dock_widget)
            dock_widget.hide()

        for i, widget_name in enumerate(widget_name_list):
            self.ui_window.addDockWidget(target_location[i], self.ui_window.docking_widgets[widget_name])  # 변경된 위치로 이동
            self.ui_window.docking_widgets[widget_name].show()

        self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"], Qt.Vertical)
        self.ui_window.resizeDocks(
            [self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"]], 
            [1, 1],
            Qt.Vertical
        )
        
        # Clear central layout
        PyQtAddon.clear_layout(self.ui_window.central_layout)
        
        # Central layout에 training_plot_canvas 배치
        self.ui_window.central_layout.addWidget(self.training_plot_canvas)
        
    def on_app_exit(self):
        """app 종료 시 호출되는 이벤트"""
        return

def main():
    current_file_path = os.path.dirname(os.path.abspath(__file__)) # 현재 파일 경로 반환
    data_directory = os.path.dirname(current_file_path) # 현재 파일 경로의 상위 경로 반환
    AppManager(data_directory)

if __name__ == "__main__":
    main()