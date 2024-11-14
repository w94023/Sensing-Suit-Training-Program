from lib.base import *
from lib.pyqt_base import *

from lib.scr.pyqt import *
from lib.scr.json import *
from lib.scr.optimization import *

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
        self.ui_window.add_docking_widget("Optimized data",        Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Optimized data viewer", Qt.RightDockWidgetArea)
        
        self.ui_window.docking_widgets["Data"].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)  # 레이아웃 정책 설정
        self.ui_window.docking_widgets["Data viewer"].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)  # 레이아웃 정책 설정

        
        # File tree viewer + file browser 생성 후 layout에 배치
        file_viewer = CustomFileSystemWidget(self.target_directory)
        self.ui_window.docking_widgets["Directory"].setWidget(file_viewer)
        
        json_data_manager = JSONDataManager()

        # JSON 뷰어 배치
        json_list_viewer = JSONListViewer(json_data_manager, parent=self.ui_window)
        self.ui_window.docking_widgets["Data"].setWidget(json_list_viewer)

        # JSON data 뷰어 배치
        json_data_viewer = JSONDataViewer(json_data_manager, json_list_viewer, parent=self.ui_window)
        self.ui_window.docking_widgets["Data viewer"].setWidget(json_data_viewer)

        # # Logger layout에 배치
        # self.logger = CustomLogger()
        # self.ui_window.docking_widgets["Log"].setWidget(self.logger)

        # JSON Data plot widget 생성 및 배치
        json_data_plotter = JSONDataPlotter(json_data_manager, json_data_viewer, parent=self.ui_window)
        json_data_plot_canvas = json_data_plotter.get_figure_widget()
        self.ui_window.docking_widgets["Labels"].setWidget(json_data_plotter)
        
        # data refining widget 배치
        data_edit_widget = DataEditWidget(json_data_manager, json_data_viewer, json_data_plotter, parent=self.ui_window)
        self.ui_window.docking_widgets["Data edit"].setWidget(data_edit_widget)

        optimizer_widget = OptimizationWidget(self.optimization_result_directory, json_data_manager, json_data_viewer, parent=self.ui_window)
        self.ui_window.docking_widgets["Optimization"].setWidget(optimizer_widget)

        ############# optimization data viewer 생성 ##################
        optimization_result_list_viewer = OptimizationResultFileListViewer(self.optimization_result_directory, parent=self.ui_window)
        self.ui_window.docking_widgets["Optimized data"].setWidget(optimization_result_list_viewer)
        
        optimization_result_data_viewer = OptimizationResultFileListViewer(self.optimization_result_directory, parent=self.ui_window)
        self.ui_window.docking_widgets["Optimized data viewer"].setWidget(optimization_result_data_viewer)

        self.ui_window.central_layout.addWidget(json_data_plot_canvas)
        
        preparation_layout_action = QAction("Preparation", self.ui_window)
        preparation_layout_action.triggered.connect(self.__set_preparation_layout)
        self.ui_window.layout_menu.addAction(preparation_layout_action)
        
        optimization_layout_action = QAction("Optimization", self.ui_window)
        optimization_layout_action.triggered.connect(self.__set_optimization_layout)
        self.ui_window.layout_menu.addAction(optimization_layout_action)
        
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
        
    def __set_optimization_layout(self):
        widget_name_list = ["Data", "Data viewer", "Optimization", "Optimized data", "Optimized data viewer"]
        target_location = [Qt.LeftDockWidgetArea, Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea, Qt.RightDockWidgetArea, Qt.RightDockWidgetArea]
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
        self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Optimization"], self.ui_window.docking_widgets["Optimized data"], Qt.Horizontal)
        self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Optimized data"], self.ui_window.docking_widgets["Optimized data viewer"], Qt.Vertical)
        self.ui_window.resizeDocks(
            [self.ui_window.docking_widgets["Optimized data"], self.ui_window.docking_widgets["Optimized data viewer"]], 
            [1, 1],
            Qt.Vertical
        )
        # if callback is not None:
        #     callback()

        # self.ui_window.add_layout_configuration("Preparation", [
        #     self.ui_window.docking_widgets["Directory"],
        #     self.ui_window.docking_widgets["Data"],
        #     self.ui_window.docking_widgets["Data viewer"],
        #     self.ui_window.docking_widgets["Labels"],
        #     self.ui_window.docking_widgets["Data edit"],
        # ], [
        #     Qt.LeftDockWidgetArea,
        #     Qt.RightDockWidgetArea,
        #     Qt.RightDockWidgetArea,
        #     Qt.RightDockWidgetArea,
        #     Qt.RightDockWidgetArea,
        # ], lambda: {
        #     # Data widget, Labels widget, Data refining widget 가로 배치 설정
        #     self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Labels"], Qt.Horizontal),
        #     self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Labels"], self.ui_window.docking_widgets["Data edit"], Qt.Horizontal),
            
        #     # Data widget, Data viewer widget 세로 배치 설정
        #     self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"], Qt.Vertical),
            
        #     # PyQtAddon.clear_layout(self.ui_window.central_layout),
        # })

        # self.ui_window.add_layout_configuration("Optimization", [
        #     self.ui_window.docking_widgets["Data"],
        #     self.ui_window.docking_widgets["Data viewer"],
        #     self.ui_window.docking_widgets["Optimization"],
        #     self.ui_window.docking_widgets["Optimized data"]
        # ], [
        #     Qt.LeftDockWidgetArea,
        #     Qt.LeftDockWidgetArea,
        #     Qt.RightDockWidgetArea,
        #     Qt.RightDockWidgetArea
        # ], lambda: {
        #     # Data widget과 Data viewer widget 세로로 나란히 배치
        #     self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"], Qt.Vertical),
        #     # 크기를 1:1 비율로 설정
        #     self.ui_window.resizeDocks([self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"]], [1, 1], Qt.Vertical),
        
        #     self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Optimization"], self.ui_window.docking_widgets["Optimized data"], Qt.Horizontal),
        #     # self.ui_window.resizeDocks([self.ui_window.docking_widgets["Optimization"], self.ui_window.docking_widgets["Optimized data"]], [1, 1], Qt.Horizontal),


        #     # PyQtAddon.clear_layout(self.ui_window.central_layout),
        #     # self.ui_window.central_layout.addWidget(json_data_show_widget)
        # })

        # self.ui_window.activate_layout("Preparation")
        
    def on_app_exit(self):
        """app 종료 시 호출되는 이벤트"""
        return

# def data_load_for_training(data_directory, ui_window, logger):
#     # global training_manager
#     print('1')
#     training_manager = TrainingManager(file_path=data_directory, progress_bar_header_width=100, ui_window=ui_window, logger=logger)
#     print('2')
#     # training_manager.load_training_data(["AA", "FE", "ML", "CB1", "CB2", "CB3", "VALID", "TEST1", "TEST2", "TEST3"])
#     training_manager.load_training_data(["AA", "VALID", "CB1"])
#     print('3')

# def training(data_directory, ui_window, logger):
#     global training_manager
#     training_manager.train_model(epoch=10, learning_rate=0.001)

def main():
    current_file_path = os.path.dirname(os.path.abspath(__file__)) # 현재 파일 경로 반환
    data_directory = os.path.dirname(current_file_path) # 현재 파일 경로의 상위 경로 반환
    AppManager(data_directory)

if __name__ == "__main__":
    main()