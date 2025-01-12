from ....pyqt_base import *
from ....ui_common import *

import random

class AnimatedAxis():
    def __init__(self, canvas, fig, ax, line_color, do_scatter):
        # animation 생성을 위한 인스턴스 저장
        self.canvas = canvas
        self.fig = fig
        self.ax = ax
        self.line = None
        
        self.data_num = 100
        self.line_color = line_color
        self.do_scatter = do_scatter
        
        # data 생성
        self.x_data = [np.nan]
        self.y_data = [np.nan]
        self.y_max = 1
        self.ax.set_xlim(0, self.data_num)
        self.ax.set_ylim(0, 1)
        self.line, = self.ax.plot(self.x_data, self.y_data, color=line_color)
        if do_scatter:
            self.scatter = self.ax.scatter([], [], color=line_color)
        else:
            self.scatter = None
        
        # Y axis auto scale 여부
        self.auto_scale_y_axis = True
        
        # animation start, stop 제어를 위한 flag 선언
        self.start_animation_flag = False
        
        # 애니메이션 생성
        self.ani = FuncAnimation(self.fig, self.update_plot, frames=itertools.count(), interval=16, blit=True, save_count=50)
        
    def update_plot(self, frame):
        """매 프레임마다 y값을 업데이트하는 함수"""
        # Line 업데이트
        self.line.set_data(self.x_data, self.y_data)
        
        # Scatter 업데이트: 기존 scatter를 삭제하고 다시 생성
        if self.do_scatter:
            if self.scatter:
                self.scatter.remove()  # 이전 scatter 삭제
            self.scatter = self.ax.scatter(self.x_data, self.y_data, color=self.line_color)
        
        if self.auto_scale_y_axis:
            if not np.all(np.isnan(self.y_data)):
                y_max = np.nanmax(self.y_data)
                if y_max > self.y_max * 2 or y_max * 2 < self.y_max:
                    self.y_max = y_max
                    self.ax.set_ylim(0, self.y_max * 2) # 약간의 여유를 두고 설정
                    self.canvas.draw()

        if self.do_scatter:
            return self.line, self.scatter
        else:
            return self.line,
    
    def set_auto_scale(self, enable):
        self.auto_scale_y_axis = enable
    
    def add_plot(self, y_value):
        self.y_data.append(y_value)
        if (len(self.y_data) > self.data_num):
            self.y_data.pop(0)
            
        self.x_data = list(range(len(self.y_data)))
        
    def set_plot(self, x_data, y_data):
        self.x_data = x_data
        self.y_data = y_data
        
    def clear(self):
        self.x_data.clear()
        self.y_data.clear()
        
class CustomFigureCanvasWorker(QThread):
    draw_request = pyqtSignal()
    
    def draw(self):
        self.draw_request.emit()
    
class CustomFigureCanvas(FigureCanvas):
    """클래스 메서드"""
    def set_custom_ax(ax):
        # 배경색 설정
        ax.set_facecolor(PyQtAddon.get_color("background_color", option=1))
        # 축 틱과 틱 레이블 색상 설정
        ax.tick_params(axis='x', colors='white')  # x축 틱 색상 설정
        ax.tick_params(axis='y', colors='white')  # y축 틱 색상 설정
        for label in ax.get_xticklabels():
            label.set_fontfamily(PyQtAddon.text_font)  # x축 틱 레이블의 글씨체 설정
        for label in ax.get_yticklabels():
            label.set_fontfamily(PyQtAddon.text_font)  # y축 틱 레이블의 글씨체 설정
        # 축 스파인(외곽선) 색상 설정
        ax.spines['bottom'].set_color(PyQtAddon.get_color("axis_color_2", option=1))  # 아래쪽 축 색상
        ax.spines['top'].set_color(PyQtAddon.get_color("axis_color_2", option=1))     # 위쪽 축 색상
        # ax.spines['left'].set_color('white')    # 왼쪽 축 색상
        # ax.spines['right'].set_color('white')   # 오른쪽 축 색상
        
    def remove_xlabels(ax):
        ax.tick_params(axis='x', which='both', left=False)
        ax.set_xticklabels([])

    def remove_ylabels(ax):
        ax.tick_params(axis='y', which='both', left=False)
        ax.set_yticklabels([])
        
    """인스턴스 메서드"""
    def __init__(self, parent=None, padding=(0.05, 0.95, 0.95, 0.05)):
        """Figure 생성"""
        self.fig = Figure()
        # Canvas 초기화
        super().__init__(self.fig)
        # 배경색 설정
        self.fig.patch.set_facecolor(PyQtAddon.get_color("background_color", option=1))
        
        # 여백 줄이기
        self.fig.subplots_adjust(left=padding[0], right=padding[1], top=padding[2], bottom=padding[3])
        
        # parent 설정
        if parent:
            self.setParent(parent)
            
        self.setStyleSheet(f"""background-color:{PyQtAddon.get_color("background_color")}; border:none;""")
        
    def set_grid(self, nrows, ncols, **kwargs):
        gridspec_params = ['wspace', 'hspace']
        # kwargs에서 GridSpec에 필요한 매개변수만 추출
        gridspec_kwargs = {k: v for k, v in kwargs.items() if k in gridspec_params and v is not None}
        self.grid = plt.GridSpec(nrows, ncols, **gridspec_kwargs) # grid 정보 반환

    def get_ani_ax(self, row, col, line_color, do_scatter=False):
        ax = self.fig.add_subplot(self.grid[row, col])
        CustomFigureCanvas.set_custom_ax(ax)
        return ax, AnimatedAxis(self, self.fig, ax, line_color, do_scatter)
        
    def get_ax(self, row, col):
        ax = self.fig.add_subplot(self.grid[row, col])
        CustomFigureCanvas.set_custom_ax(ax)
        return ax
    
    def clear(self):
        """Figure 객체에서 모든 서브플롯을 삭제하는 함수"""
        while self.fig.axes:
            self.fig.delaxes(self.fig.axes[0])  # 첫 번째 subplot을 삭제