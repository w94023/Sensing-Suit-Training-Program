from lib.base import *
from lib.pyqt_base import *

from lib.scr.pyqt import *
from lib.scr.json import *
from lib.scr.optimization import *

class AppManager():
    def __init__(self, target_directory):
        # 화면 설정
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # DPI 스케일링 활성화
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # 고해상도 DPI에 맞게 이미지도 스케일링

        # Application 생성
        app = QApplication(sys.argv)
        
        # Initial 디렉토리 저장
        self.target_directory = target_directory
        
        # Main window 생성 및 최대화
        self.ui_window = CustomMainWindow("Sensor demo program")
        self.ui_window.showMaximized()
        
        # 백그라운드 이벤트 수행을 위한 flag 초기화
        self.step_count = 0
        self.step_done = True
        self.step_processing = False
        self.background_flag = True
        
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
        self.ui_window.add_docking_widget("Directory",       Qt.LeftDockWidgetArea)
        self.ui_window.add_docking_widget("Data",            Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Data viewer",     Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Labels",          Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Data refining",   Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Optimization",    Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Data split",      Qt.RightDockWidgetArea)
        self.ui_window.add_docking_widget("Log",             Qt.BottomDockWidgetArea)
        
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
        
        # data refining widget 배치
        data_refiner = DataRefiningWidget(json_data_manager, json_data_viewer, parent=self.ui_window)
        self.ui_window.docking_widgets["Data refining"].setWidget(data_refiner)
        
        # Logger layout에 배치
        self.logger = CustomLogger()
        self.ui_window.docking_widgets["Log"].setWidget(self.logger)

        # JSON Data plot widget 생성 및 배치
        json_data_plot_widget = JSONDataPlotter(json_data_manager, json_data_viewer, parent=self.ui_window)
        json_data_plot_canvas = json_data_plot_widget.get_figure_widget()
        self.ui_window.docking_widgets["Labels"].setWidget(json_data_plot_widget)

        optimizer_widget = OptimalSensorPlacementWidget()
        self.ui_window.docking_widgets["Optimization"].setWidget(optimizer_widget)
        
        data_split_widget = DataSplittingWidget(json_data_manager, json_data_viewer, json_data_plot_widget, parent=self.ui_window)
        self.ui_window.docking_widgets["Data split"].setWidget(data_split_widget)
        
        self.ui_window.central_layout.addWidget(json_data_plot_canvas)

        self.ui_window.add_layout_configuration("Data load", [
            self.ui_window.docking_widgets["Directory"],
            self.ui_window.docking_widgets["Data"],
            self.ui_window.docking_widgets["Data viewer"],
            self.ui_window.docking_widgets["Labels"],
            self.ui_window.docking_widgets["Data refining"],
            self.ui_window.docking_widgets["Data split"],
        ], [
            Qt.LeftDockWidgetArea,
            Qt.RightDockWidgetArea,
            Qt.RightDockWidgetArea,
            Qt.RightDockWidgetArea,
            Qt.RightDockWidgetArea,
            Qt.RightDockWidgetArea
        ], lambda: {
            # Data widget과 Labels widget 가로로 나란히 배치
            self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Labels"], Qt.Horizontal),
            # Labels widget과 Data refining 가로로 나란히 배치
            self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Labels"], self.ui_window.docking_widgets["Data refining"], Qt.Horizontal),
            # Data widget과 Data viewer widget 세로로 나란히 배치
            self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"], Qt.Vertical),
            # Data refining widget과 Data split widget 세로로 나란히 배치
            self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data refining"], self.ui_window.docking_widgets["Data split"], Qt.Vertical),
            
            # PyQtAddon.clear_layout(self.ui_window.central_layout),
            
        })

        self.ui_window.add_layout_configuration("Optimization", [
            self.ui_window.docking_widgets["Data"],
            self.ui_window.docking_widgets["Data viewer"],
            self.ui_window.docking_widgets["Optimization"]
        ], [
            Qt.LeftDockWidgetArea,
            Qt.LeftDockWidgetArea,
            Qt.RightDockWidgetArea,
        ], lambda: {
            # Data widget과 Data viewer widget 세로로 나란히 배치
            self.ui_window.splitDockWidget(self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"], Qt.Vertical),
            # 크기를 1:1 비율로 설정
            self.ui_window.resizeDocks([self.ui_window.docking_widgets["Data"], self.ui_window.docking_widgets["Data viewer"]], [1, 1], Qt.Vertical)


            # PyQtAddon.clear_layout(self.ui_window.central_layout),
            # self.ui_window.central_layout.addWidget(json_data_show_widget)
        })

        self.ui_window.activate_layout("Data load")
        
        # # Control button 생성 후 이벤트 연결, layout 배치
        # control_buttons = CustomControlButtons(self.set_next_step)
        # self.ui_window.layouts["Control buttons"].content_layout.addWidget(control_buttons)
        
        # # Layout initialization
        # PyQtAddon.remove_all_widgets_in_layout(CustomNoDataWidget(), self.ui_window.central_layout)
        # PyQtAddon.remove_all_widgets_in_layout(CustomNoDataWidget(), self.ui_window.layouts["Progress"])
            
    # def background_task(self):
    #     """UI 업데이트는 메인 스레드에서 진행, 작업은 백그라운드 스레드에서 진행"""
    #     """백그라운드 스레드에서는 등록된 callback들을 수행함"""
        
    #     # 메인스레드에서 UI 생성
    #     self.ui_window.worker.set(self.create_ui)
    #     time.sleep(0.1)
        
    #     while self.background_flag:
    #         if not self.step_done:
    #             if self.step_count-1 >= len(self.background_callbacks):
    #                 self.logger.worker.add_log("All registered functions have been executed.")
    #                 break
                    
    #             self.step_processing = True
    #             self.background_callbacks[self.step_count-1](self.target_directory, self.ui_window, self.logger)
    #             self.step_processing = False
    #             self.step_done = True
                
    # def set_next_step(self):
    #     """Control button 클릭 시 백그라운드 스레드에서 등록된 다음 callback을 실행시키는 이벤트"""
    #     if not self.step_processing and self.step_done:
    #         self.step_count += 1
    #         self.step_done = False
    #     else:
    #         self.logger.worker.add_error_log("The previously requested process is already in progress.")
            
    def on_app_exit(self):
        """app 종료 시 호출되는 이벤트"""
        self.background_flag = False
        # self.thread.join()

# def data_management(data_directory, ui_window, logger):
#     data_manager = DataManager(data_directory, 100, ui_window, logger)

# def data_split(data_directory, ui_window, logger):
#     data_splitter = Data_Splitter(file_path=data_directory, progress_bar_header_width=100, ui_window=ui_window, logger=logger)
#     data_splitter.split_test_data("TEST1_original", 60, "VALID", "TEST1")

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
    
    # # 모든 함수 리스트에서 main을 제외한 함수만 추가
    # def collect_methods_from_main_file():
    #     method_list = []

    #     # 현재 모듈에서 정의된 모든 함수들을 확인
    #     for name, obj in globals().items():
    #         if callable(obj):  # 함수인지 확인
    #             # 해당 함수가 현재 파일에서 정의되었는지 확인
    #             if inspect.getmodule(obj).__file__ == __file__:
    #                 if name != 'main':  # main을 제외한 함수만 리스트에 추가
    #                     method_list.append(obj)
                        
    #     return method_list

    # background_callbacks = collect_methods_from_main_file()[1:] # AppManager의 __init__ 메서드 제외
    AppManager(data_directory)

if __name__ == "__main__":
    main()