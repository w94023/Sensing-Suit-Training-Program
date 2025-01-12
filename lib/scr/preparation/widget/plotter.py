from .common import *
from ...pyqt.widget import (CustomDataTreeView, CustomFigureCanvas)

class PreparationDataPlotter(QWidget):
    def __init__(self, data_handler, data_viewer, parent=None):
        """JSON 데이터 내 선택된 column을 플랏하는 위젯

        Args:
            data_handler (CustomJSONDataManager): JSON 데이터 불러오기 위한 인스턴스 참조
            data_viewer (CustomJSONDataViewer): JSON 데이터 더블 클릭 이벤트 수신을 위한 인스턴스
            parent (QWidget, optional): 부모 객체. Defaults to None.
        """
        
        self.parent = parent
        super().__init__(parent)
        
        # 인스턴스 저장
        self.data_handler = data_handler
        self.data_viewer = data_viewer
        self.data_viewer.on_item_double_clicked += self.__on_plot_data_selected
        
        # canvas 좌우상하 패딩 설정
        self.canvas_padding = (0.15, 0.95, 0.95, 0.05)
        
        # UI 초기화
        self.__init_ui()
        
        # 다른 위젯에 배치할 캔버스 위젯 생성
        self.__create_figure_widget()
            
        # TreeView 이벤트 연결
        self.tree_view.on_item_clicked += self.__on_plot_label_changed
        
        # 인스턴스 저장 데이터
        self.target_file_data = None
        self.target_file_type = None
        self.target_file_data_ylim = []
        
        self.ax = None
        
    def get_figure_widget(self):
        """Legend widget, canvas가 배치된 widget 반환"""
        return self.figure_widget
 
    def __clear(self):
        """TreeView, Canvas, 인스턴스 데이터 모두 초기화"""
        self.target_file_data = None
        self.target_file_type = None
        self.target_file_data_ylim.clear()
        
        self.tree_view.clear_itmes()
        self.__clear_canvas()
        
    def __clear_canvas(self):
        """Canvas만 초기화"""
        self.ax = None
        self.legend_widget.clear_layout()
        self.canvas.clear()
        self.canvas.draw()
        
    def __on_plot_data_selected(self, header):
        """선택된 데이터 저장 및 TreeView에 column 표시

        Args:
            header (str list): 타겟 데이터를 찾기 위한 dictionary key 생성을 위한 헤더
        """
        
        if header is None:
            self.__clear()
            return
    
        if len(header) != 3:
            self.__clear()
            return
        
        # header를 통해 dictionary key 생성
        data_key = header[0]+"-"+header[1]+"-"+header[2]
        
        # header로 file type 구분
        self.target_file_type = header[1] # "marker" or "sensor"
        
        # dictionary 형태로 구성된 데이터 받아오기
        data = self.data_handler.file_data
        
        # dictionary key가 data 내에 존재하는 지 확인
        if data_key not in data.keys():
            return
        
        # Target data의 column 추출
        target_data = data[data_key]
        columns = target_data.columns.tolist()[1:] # 첫 열은 제외 (Time)
        
        # TreeView item 생성
        tree_view_item = []
        for i in range(len(columns)):
            tree_view_item.append([str(i), columns[i]])
        
        # TreeView item 추가
        self.tree_view.add_items(tree_view_item, [False]*len(tree_view_item), [False]*len(tree_view_item))
        
        # 데이터 저장
        self.target_file_data = target_data
        
    def __on_plot_label_changed(self, item_names):
        """TreeView에서 column이 선택되었을 때, canvas에서 plot을 생성하는 메서드

        Args:
            item_names (list): [index, label]을 멤버로 가지는 선택된 항목 리스트
        """
        
        def add_offset_to_limit(limit, ratio):
            new_limit = [0, 0]

            span = limit[1]-limit[0]
            new_limit[0] = limit[0] - span * ratio
            new_limit[1] = limit[1] + span * ratio

            return new_limit
        
        if item_names is None:
            self.__clear_canvas()
            return
            
        if len(item_names) == 0:
            self.__clear_canvas()
            return
        
        # Plot canvas 초기화
        self.canvas.clear()
        
        # Axis 생성
        self.ax = self.canvas.get_ax(0, 0)
        
        # x, y label 및 title 추가
        if self.target_file_type == "marker":
            self.ax.set_title("Marker data plot", color=UiStyle.get_color("content_text_color", "fraction"))
            self.ax.set_xlabel("Time (s)",        color=UiStyle.get_color("content_text_color", "fraction"))
            self.ax.set_ylabel("Position (mm)",   color=UiStyle.get_color("content_text_color", "fraction"))
        elif self.target_file_type == "sensor":
            self.ax.set_title("Sensor data plot", color=UiStyle.get_color("content_text_color", "fraction"))
            self.ax.set_xlabel("frame",           color=UiStyle.get_color("content_text_color", "fraction"))
            self.ax.set_ylabel("Digit",           color=UiStyle.get_color("content_text_color", "fraction"))
        
        # 선택된 데이터 plot
        for i in range(len(item_names)):
            label = item_names[i][1] # [0] : index, [1] : label
            
            # y max 설정을 위한 min, max 계산
            min, max = self.target_file_data[label].min(), self.target_file_data[label].max()
            
            # 설정된 y max가 없을 경우 새로 생성
            if len(self.target_file_data_ylim) == 0:
                self.target_file_data_ylim = [min, max]
            else:
                # Y max 최신화
                if self.target_file_data_ylim[0] > min:
                    self.target_file_data_ylim[0] = min
                if self.target_file_data_ylim[1] < max:
                    self.target_file_data_ylim[1] = max

            self.ax.plot(self.target_file_data.iloc[:, 0], self.target_file_data[label], color=UiStyle.get_plot_color(i), label=label)
            self.ax.set_ylim(add_offset_to_limit(self.target_file_data_ylim, 0.1))
            self.canvas.draw()
            
        # plot의 legend 핸들과 레이블을 가져오기
        handles, labels = self.ax.get_legend_handles_labels()
    
        # Legend 생성
        self.legend_widget.set_legend(handles, labels)
        
    def __init_ui(self):
        """위젯 UI 초기화"""
        # 레이아웃 설정
        layout = QVBoxLayout()
        
        # 위젯 스타일 설정
        self.setLayout(layout)
        self.setStyleSheet(f"""
                            QWidget {{
                                margin: 0px;
                                padding: 0px;
                                background-color: {UiStyle.get_color("background_color")};
                                }}""")
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 10, 0, 10)
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget)

        # TreeView 생성
        self.tree_view = CustomDataTreeView(["Index", "Label"], parent=self.parent)
        self.tree_view.enable_header(True)
        self.tree_view.enable_double_click_event(False)
        content_layout.addWidget(self.tree_view)
        
    def __create_figure_widget(self):
        """다른 위젯에 배치할 legend_widget+canvas 위젯 생성"""
        # Figure widget 생성
        self.figure_widget = QWidget()
        figure_layout = QVBoxLayout()
        self.figure_widget.setLayout(figure_layout)
        
        # Canvas  생성
        self.canvas = CustomFigureCanvas(padding=self.canvas_padding, parent=self.parent)
        self.canvas.set_grid(1, 1)

        # Legend widget 생성
        self.legend_widget = CustomLegendWidget(self.parent)
        
        # 레이아웃 추가
        figure_layout.addWidget(self.legend_widget, 1)
        figure_layout.addWidget(self.canvas, 10)