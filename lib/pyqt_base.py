from .base import *

import os
import time
import itertools
import re # 정규 표현식 비교
from functools import partial # 슬롯 메서드에 매개변수 전달

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import uic
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from PyQt5.QtCore import (Qt, QSize, QThread, pyqtSignal, QUrl, QDir, QMimeData,
                          QFileSystemWatcher, QTimer, QMutex, QWaitCondition, QByteArray,
                          QRect, QRectF, QMetaObject, QObject, QEvent)
from PyQt5.QtGui import  (QIcon, QPixmap, QStandardItem, QStandardItemModel, QFontMetrics,
                          QDragEnterEvent, QDragMoveEvent, QDropEvent, QFont, QColor, 
                          QDrag, QBrush, QPen, QPainter, QMovie, QMouseEvent)
from PyQt5.QtWidgets import (QApplication, QLabel, QCalendarWidget, QFrame, QTreeView,
                             QTableWidget, QFileSystemModel, QPlainTextEdit, QToolBar,
                             QWidgetAction, QComboBox, QAction, QSizePolicy, QInputDialog,
                             QWidget, QTextEdit, QMainWindow, QDockWidget, QHBoxLayout,
                             QVBoxLayout, QToolButton, QPushButton, QProgressBar, QSpacerItem,
                             QScrollArea, QFileDialog, QTableWidgetItem, QListWidget, QListWidgetItem,
                             QHeaderView, QMessageBox, QStyledItemDelegate, QStyleOptionViewItem,
                             QGridLayout, QDialog, QLineEdit, QListView, QMenu, QDialogButtonBox, QLayout,
                             QTabWidget)
                      
#############################################
#             디렉토리 설정                 #
#############################################
current_directory = os.path.dirname(__file__)
fonts_directory = os.path.join(current_directory, 'fonts')
icons_directory = os.path.join(current_directory, 'icons')

def hide_widgets(layout):
    """현재 레이아웃의 모든 위젯을 삭제하고 초기화하는 메서드"""
    while layout.count():
        item = layout.takeAt(0)  # 첫 번째 아이템을 가져옴
        widget = item.widget()
        if widget is not None:
            widget.setVisible(False)
        else:
            # QLayout일 경우, 재귀적으로 내부 위젯도 삭제
            hide_widget_item(item.layout())
            
def hide_widget_item(layout):
    """내부 레이아웃의 모든 위젯도 삭제"""
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setVisible(False)
            elif item.layout() is not None:
                hide_widget_item(item.layout())  # 내부 레이아웃에 대해 재귀적으로 삭제
                
def show_widgets(layout):
    """현재 레이아웃의 모든 위젯을 삭제하고 초기화하는 메서드"""
    while layout.count():
        item = layout.takeAt(0)  # 첫 번째 아이템을 가져옴
        widget = item.widget()
        if widget is not None:
            widget.setVisible(True)
        else:
            # QLayout일 경우, 재귀적으로 내부 위젯도 삭제
            show_widget_item(item.layout())
            
def show_widget_item(layout):
    """내부 레이아웃의 모든 위젯도 삭제"""
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setVisible(True)
            elif item.layout() is not None:
                show_widget_item(item.layout())  # 내부 레이아웃에 대해 재귀적으로 삭제
                
def delete_widgets(layout):
    """현재 레이아웃의 모든 위젯을 삭제하고 초기화하는 메서드"""
    while layout.count():
        item = layout.takeAt(0)  # 첫 번째 아이템을 가져옴
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()  # 위젯 삭제
        else:
            # QLayout일 경우, 재귀적으로 내부 위젯도 삭제
            delete_widget_item(item.layout())
                
def delete_widget_item(layout):
    """내부 레이아웃의 모든 위젯도 삭제"""
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # 위젯 삭제
            elif item.layout() is not None:
                delete_widget_item(item.layout())  # 내부 레이아웃에 대해 재귀적으로 삭제
                    
#############################################
#               폰트 설치                   #
#############################################
check_and_install_oxanium_font()

#############################################
#                PyQt 애드온                #
#############################################
class PyQtAddon():
    """애드온 메서드"""
    # Layout 초기화
    def remove_all_widgets_in_layout(no_data_widget, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        layout.addWidget(no_data_widget)
    
    # Layout 초기화 (위젯 삭제 x)
    def clear_layout(layout):
        """Layout의 모든 위젯을 레이아웃에서 제거하여 초기화"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # 레이아웃에서 위젯 제거 (삭제하지 않음)
                layout.removeWidget(widget)
                widget.setParent(None)
            
    # Layout 초기화 (위젯 삭제 o)
    def init_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            
    # svg 파일 import를 위한 파일 경로 획득
    # 파일 경로에 빈칸, 한글이 포함되어 있을 경우, url로 변환해야 함
    def convert_url(path):
        return QUrl.fromLocalFile(path).toLocalFile()
    
    def create_svg_icon(image_name, width, height):
        """icons_directory에 존재하는 icon으로 QIcon 생성하는 메서드 

        Args:
            image_name: source image 이름
            width: icon 너비
            height: icon 높이
        """
        image_path = PyQtAddon.convert_url(os.path.join(icons_directory, image_name))
        
        return QIcon(QPixmap(image_path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def create_svg_widget(image_name, width, height, size_policy_x=QSizePolicy.Fixed, size_policy_y=QSizePolicy.Fixed):
        """icons_directory에 존재하는 icon으로 QSvgWidget 생성하는 메서드 

        Args:
            image_name: source image 이름
            width: icon 너비
            height: icon 높이
            size_policy_x: x방향 size policy. Defaults to QSizePolicy.Fixed
            size_policy_y: y방향 size policy. Defaults to QSizePolicy.Fixed
        """
        image_path = PyQtAddon.convert_url(os.path.join(icons_directory, image_name))
        
        svg_widget = QSvgWidget(image_path)
        svg_widget.setFixedSize(width, height)
        svg_widget.setSizePolicy(size_policy_x, size_policy_y)
        svg_widget.setStyleSheet("border:none")
        
        return svg_widget
        
    
    def set_button_icon(button, image_name, width, height):
        """
        버튼에 PNG 이미지를 설정하고 크기에 맞게 조정하는 함수
        :param button: QPushButton 객체
        :param image_name: 이미지 이름
        :param width: 버튼 너비
        :param height: 버튼 높이
        """
        image_path = PyQtAddon.convert_url(os.path.join(icons_directory, image_name))
        
        icon = QIcon(QPixmap(image_path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        button.setIcon(icon)
        button.setIconSize(QSize(width, height))  # 버튼의 아이콘 크기를 버튼 크기에 맞게 설정
        button.setFixedSize(width, height)  # 버튼의 크기를 고정
    
    colors = {}
    @classmethod
    def get_color(cls, label, option=0):
        # option=0 : rgba as string           ("rgba(100, 200, 255, 1)")
        # option=1 : rgba as normalized tuple ((100/255, 200/255, 255/255, 1))
        if option == 0:  
            return f"""rgba{
                cls.colors[label][0],
                cls.colors[label][1],
                cls.colors[label][2],
                cls.colors[label][3]
                }"""
        elif option == 1:
            return (cls.colors[label][0]/255,
                    cls.colors[label][1]/255, 
                    cls.colors[label][2]/255, 
                    cls.colors[label][3])
        elif option == 2:
            return QColor(
                cls.colors[label][0],
                cls.colors[label][1], 
                cls.colors[label][2], 
                int(cls.colors[label][3]*255)
            )

    """UI 스타일 정의"""
    # Window 설정
    main_window_width = 1960
    main_window_height = 1080
    # 폰트
    text_font = "Arial"
    # UI 컬러 스타일
    colors["background_color"]            = (0,   0,   0,   1  ) # app의 background color
    colors["line_color"]                  = (76,  76,  76,  1  ) # layout 간 구별을 위해 사용되는 line의 color
    colors["content_line_color"]          = (76,  76,  76,  0.5) # layout 내에 사용되는 옅은 line color
    colors["title_text_color"]            = (255, 255, 255, 1  ) # layout title에 사용되는 text color
    colors["title_bar_color"]             = (31,  91,  92,  1  ) # layout title bar에 사용되는 color
    colors["content_text_color"]          = (255, 255, 255, 0.5) # layout 내 content 표시에 사용되는 text color (title_text_color보다 연하게 설정)
    colors["content_hover_color"]         = (76,  76,  76,  0.5) # layout 내에서 선택 가능한 항목에 마우스 hover 시 사용되는 color
    colors["error_text_color"]            = (255, 0,   0,   0.6) # 특히 log에서, 에러가 발생했을 때 출력하는 text의 color (붉은 계열 색으로 설정)
    colors["minimize_button_hover_color"] = (100, 100, 100, 0.4) # layout title bar의 minimize button 마우스 hover 시 사용되는 color
    colors["close_button_hover_color"]    = (255, 0,   0,   0.4) # layout title bar의 close button 마우스 hover 시 사용되는 color
    # Plot 컬러 스타일
    colors["point_color_1"]               = (100, 100, 100, 0.5) # 회색
    colors["point_color_2"]               = (0,   120, 212, 0.5) # 파란색
    colors["point_color_3"]               = (252, 88,  126, 1  ) # 분홍색
    colors["point_color_4"]               = (234, 23,  12,  1  ) # 붉은색
    colors["point_color_5"]               = (31,  91,  92,  0.5) # 투명한 청록색
    colors["point_color_6"]               = (252, 88,  126, 0.5) # 투명한 분홍색
    colors["axis_color_1"]                = (255, 255, 255, 1  ) # 하얀색
    colors["axis_color_2"]                = (76,  76,  76,  1  ) # 연한 회색
    colors["axis_color_3"]                = (150, 150, 150, 1  ) # 짙은 회색
    colors["plot_color_1"]                = (86 , 233, 255, 1  ) # 청록 계열
    colors["plot_color_2"]                = (255, 183, 57,  1  ) # 오렌지 계열
    colors["plot_color_3"]                = (222, 65,  2,   1  ) # 빨강 계열
    colors["plot_color_1_transparent"]    = (86 , 233, 255, 0.5) # 청록 계열
    colors["plot_color_2_transparent"]    = (255, 183, 57,  0.5) # 오렌지 계열
    colors["plot_color_3_transparent"]    = (222, 65,  2,   0.5) # 빨강 계열
    # Scrollbar 스타일 정의
    background_color = "rgba(0, 0, 0, 1)" # UI 컬러 스타일과 동일하게 설정
    scrollbar_width = 15
    scrollbar_minimum_height = 15
    scrollbar_handle_color = "rgba(76, 76, 76, 0.5)"
    vertical_scrollbar_style = f"""
                                /* 수직 스크롤바 */   
                                QScrollBar:vertical {{
                                    border: 1px solid {scrollbar_handle_color};
                                    background: {background_color};
                                    width: {scrollbar_width}px;
                                    margin: 0px 0px 0px 0px;
                                }}
                                /* 수직 스크롤바 핸들 */
                                QScrollBar::handle:vertical {{
                                    border: none;
                                    background-color: {scrollbar_handle_color};
                                    width: {scrollbar_width}px;
                                    min-height: {scrollbar_minimum_height}px;
                                }}
                                /* 아래 화살표 부분 */
                                QScrollBar::add-line:vertical {{
                                    border: none;
                                    background: #d3d3d3;
                                    height: 0px;
                                    subcontrol-position: bottom;
                                    subcontrol-origin: margin;
                                }}
                                /* 위 화살표 부분 */
                                QScrollBar::sub-line:vertical {{
                                    border: none;
                                    background: #d3d3d3;
                                    height: 0px;
                                    subcontrol-position: top;
                                    subcontrol-origin: margin;
                                }}
                                /* 화살표 부분 삭제 */
                                QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                                    background: none;
                                }}
                                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                                    background: none;
                                }}
                                """                  
    horizontal_scrollbar_style = f"""
                                /* 수평 스크롤바 */   
                                QScrollBar:horizontal {{
                                    border: 1px solid {scrollbar_handle_color};
                                    background: {background_color};
                                    height: {scrollbar_width}px;
                                    margin: 0px 0px 0px 0px;
                                }}
                                /* 수평 스크롤바 핸들 */
                                QScrollBar::handle:horizontal {{
                                    border: none;
                                    background-color: {scrollbar_handle_color};
                                    height: {scrollbar_width}px;
                                    min-width: {scrollbar_minimum_height}px;
                                }}
                                /* 아래 화살표 부분 */
                                QScrollBar::add-line:horizontal {{
                                    border: none;
                                    background: #d3d3d3;
                                    width: 0px;
                                    subcontrol-position: bottom;
                                    subcontrol-origin: margin;
                                }}
                                /* 위 화살표 부분 */
                                QScrollBar::sub-line:horizontal {{
                                    border: none;
                                    background: #d3d3d3;
                                    width: 0px;
                                    subcontrol-position: top;
                                    subcontrol-origin: margin;
                                }}
                                /* 화살표 부분 삭제 */
                                QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {{
                                    background: none;
                                }}
                                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                                    background: none;
                                }}
                                """

#############################################
#            PyQt 클래스 재정의             #
#############################################
"""FigureCanvas 재정의""" 
class AnimatedAxis():
    def __init__(self, canvas, fig, ax):
        # animation 생성을 위한 인스턴스 저장
        self.canvas = canvas
        self.fig = fig
        self.ax = ax
        self.line = None
        
        # data 생성
        self.x_data = [np.nan]
        self.y_data = [np.nan]
        self.y_max = 0
        self.ax.set_xlim(0, 3000)
        self.ax.set_ylim(0, 60000)
        self.line, = self.ax.plot(self.x_data, self.y_data)
        
        # animation start, stop 제어를 위한 flag 선언
        self.start_animation_flag = False

        # animation 생성
        self.ani = FuncAnimation(self.fig, self.update_plot, frames=itertools.count(), interval=16, blit=True, save_count=50)
        
    def update_plot(self, frame):
        """매 프레임마다 y값을 업데이트하는 함수"""
        self.line.set_ydata(self.y_data)
        # if not np.all(np.isnan(self.y_data)):
        #     y_max = np.nanmax(self.y_data)
        #     if y_max != self.y_max:
        #         self.y_max = y_max
        #         self.ax.set_ylim(0, self.y_max + 10) # 약간의 여유를 두고 설정
                # self.canvas.draw()

        return self.line,
    
    def start_animation(self):
        self.start_animation_flag = True
    
    def stop_animation(self):
        self.start_animation_flag = False
        # """애니메이션을 중지하는 함수"""
        # self.ani.event_source.stop()  # 애니메이션을 멈춤
        
    def set_plot(self, ndata, line_color):
        # plotting line 생성
        self.line.remove()
        self.x_data = list(range(ndata))
        self.y_data = [np.nan]*len(self.x_data)
        # self.ax.set_xlim(0, len(self.x_data))
        self.line, = self.ax.plot(self.x_data, self.y_data, color=line_color)
        
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
            
        # self.worker = CustomFigureCanvasWorker()
        # self.worker.draw_request.connect(self.draw)
        # self.worker.start()
        
    def set_grid(self, nrows, ncols, **kwargs):
        gridspec_params = ['wspace', 'hspace']
        # kwargs에서 GridSpec에 필요한 매개변수만 추출
        gridspec_kwargs = {k: v for k, v in kwargs.items() if k in gridspec_params and v is not None}
        self.grid = plt.GridSpec(nrows, ncols, **gridspec_kwargs) # grid 정보 반환

    def get_ani_ax(self, row, col):
        ax = self.fig.add_subplot(self.grid[row, col])
        CustomFigureCanvas.set_custom_ax(ax)
        return ax, AnimatedAxis(self, self.fig, ax)
        
    def get_ax(self, row, col):
        ax = self.fig.add_subplot(self.grid[row, col])
        CustomFigureCanvas.set_custom_ax(ax)
        return ax
    
    def clear(self):
        """Figure 객체에서 모든 서브플롯을 삭제하는 함수"""
        while self.fig.axes:
            self.fig.delaxes(self.fig.axes[0])  # 첫 번째 subplot을 삭제

    # def plot_error_ax(ax, time_offset, color, label):
    #     def create_arrow_point(ax, x, y, arrow_head_width, arrow_head_length):
    #         ax.add_patch(patches.FancyArrow(x, y+arrow_head_length, 0, -arrow_head_length/100, 
    #                                         width=0, head_width=arrow_head_width, head_length=arrow_head_length, color=color, zorder=3))
    #     # 데이터 표시용 화살표 만들기
    #     xlim = ax.get_xlim()
    #     ylim = ax.get_ylim()
    #     arrow_head_width = (xlim[1]-xlim[0])/60
    #     arrow_head_length = (ylim[1]-ylim[0])/5
    #     create_arrow_point(ax, time_offset, -1,                       arrow_head_width, arrow_head_length) # 1단 화살표
    #     create_arrow_point(ax, time_offset, -1+arrow_head_length*0.7, arrow_head_width, arrow_head_length) # 2단 화살표
    #     ax.text(time_offset, 0, label+"\n"+str(round(time_offset*1000))+" ms", va='bottom', ha='center', fontname=self.label_font_name, fontsize=8, color=color, zorder=3)
       
"""QHBoxLayout 재정의"""
class CustomHBoxLayout(QHBoxLayout):
    def __init__(self, parent=None):
        super().__init__()
        if parent:
            self.widget = QWidget(parent)
        else:
            self.widget = QWidget()
        self.widget.setLayout(self)
            
    def add_layout(self, layout):
        self.addWidget(layout.widget)

"""QVBoxLayout 재정의"""
class CustomVBoxLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super().__init__()
        if parent:
            self.widget = QWidget(parent)
        else:
            self.widget = QWidget()
        self.widget.setLayout(self)
            
    def add_layout(self, layout):
        self.addWidget(layout.widget)
       
"""QLabel 재정의""" 
class CustomLabelWorker(QThread):
    update_label = pyqtSignal(str)
    
    def set_text(self, text):
        self.update_label.emit(text)

class CustomLabel(QLabel):
    def __init__(self, parent=None):
        super(CustomLabel, self).__init__(parent)
        self.setStyleSheet(f"""background-color:none; color:{PyQtAddon.get_color("content_text_color")}; font-family:{PyQtAddon.text_font}""")
        
        self.worker = CustomLabelWorker()
        self.worker.update_label.connect(self.update_label_text)
        self.worker.start()
        
    def update_label_text(self, text):
        self.setText(text)

"""QTableWidget 재정의""" 
class CustomTableWidgetWorker(QThread):
    update_data = pyqtSignal(object, bool)
    
    def set_data(self, dataframe, use_vertical_header=True):
        self.update_data.emit(dataframe, use_vertical_header)
        
class CustomTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 스타일시트 적용
        self.setStyleSheet(f"""
            /* 테이블 설정 */
            QTableWidget {{
                background-color: {PyQtAddon.get_color("background_color")};  
                border-top: 1px solid {PyQtAddon.get_color("line_color")};
                border-bottom: 1px solid {PyQtAddon.get_color("line_color")};
            }}
            /* 헤더 및 인덱스 설정 */
            QHeaderView::section {{
                background-color: {PyQtAddon.get_color("title_bar_color")};
                color: {PyQtAddon.get_color("content_text_color")}; 
                font-family: {PyQtAddon.text_font};
                border:none;
            }}
            /* 행, 열 헤더 나뉘는 부분 설정 */
            QTableCornerButton::section {{
                background-color: {PyQtAddon.get_color("background_color")};  
            }}
            /* 셀 설정 */
            QTableWidget::item {{
                background-color: {PyQtAddon.get_color("background_color")};
                color: {PyQtAddon.get_color("content_text_color")};
            }}
        """)
        
        self.worker = CustomTableWidgetWorker()
        self.worker.update_data.connect(self.update_data)
        self.worker.start()
        
    def update_data(self, dataframe, use_vertical_header):
        rows, columns = dataframe.shape
        
        # 행, 열 개수 설정
        self.setRowCount(rows)
        self.setColumnCount(columns)
        
        # 테이블 헤더 str로 변환
        str_header = []
        for header in dataframe.columns:
            str_header.append(str(header))
        
        # 테이블 헤더 설정
        self.setHorizontalHeaderLabels(str_header)
        
        # 폰트 설정
        custom_font = QFont(f"{PyQtAddon.text_font}")
        
        # 테이블에 데이터추가
        for row in range(rows):
            for col in range(columns):
                # 각 셀에 DataFrame 데이터를 넣기
                item = QTableWidgetItem(str(dataframe.iat[row, col]))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(custom_font)
                self.setItem(row, col, item)
              
        self.verticalHeader().setVisible(use_vertical_header)
        
        # Table 크기로 위젯 크기 고정  
        if use_vertical_header:
            vertical_header_width = self.verticalHeader().width()
        else:
            vertical_header_width = 0

        table_width = vertical_header_width + self.horizontalHeader().length() + self.frameWidth() * 2
        table_height = self.horizontalHeader().height() + self.verticalHeader().length() + self.frameWidth() * 2
        self.setFixedSize(table_width, table_height)
   
"""CustomTitleBar 신규 정의"""      
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

"""CustomProgressBar 신규 정의 (QProgressBar + QLabel)"""  
class CustomProgressBar(QWidget):
    def __init__(self, header_width, parent=None):
        super().__init__(parent)
        
        # Layout 설정
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # header 생성
        # self.header = QLabel()
        # self.header.setText("")
        # self.header.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # self.header.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.header.setFixedSize(header_width, 20)
        # self.header.setStyleSheet(f"""
        #                           QLabel {{
        #                               background-color:{PyQtAddon.get_color("background_color")};
        #                               color:{PyQtAddon.get_color("content_text_color")};
        #                               font-family:{PyQtAddon.text_font};
        #                               }}""")
        # layout.addWidget(self.header)
        
        # ProgressBar 생성
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progress_bar.setFixedSize(0, 10)
        self.progress_bar.setMinimumSize(100, 10)
        self.progress_bar.setMaximumSize(16777215, 10)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet(f"""
                                        QProgressBar {{
                                            border-top:1px solid {PyQtAddon.get_color("line_color")};
                                            border-bottom:1px solid {PyQtAddon.get_color("line_color")};
                                            border-left:none;
                                            border-right:none;
                                            border-radius:0px;
                                            padding-top:2px;
                                            padding-bottom:2px;
                                            background-color:{PyQtAddon.get_color("background_color")};
                                            }}
                                            
                                        QProgressBar::chunk {{
                                            background-color:{PyQtAddon.get_color("line_color")};
                                            width:2.15px;
                                            margin:0.5px;
                                            }}
                                        """)
        layout.addWidget(self.progress_bar)
        
        # ProgressBar label 생성 (진행도 text로 표시)
        self.progress_label = QLabel()
        self.progress_label.setText("0%")
        # self.progress_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.progress_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.progress_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.progress_label.setFixedSize(30, 20)
        self.progress_label.setStyleSheet(f"""
                                          QLabel {{
                                              background-color:{PyQtAddon.get_color("background_color")};
                                              color:{PyQtAddon.get_color("content_text_color")};
                                              font-family:{PyQtAddon.text_font};
                                              }}""")
        layout.addWidget(self.progress_label, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Widget 그래픽 설정
        self.setStyleSheet("QWidget { margin: 0px; padding: 0px; background-color: none; }")

    def set_header(self, header):
        self.header.setText(header)

    def set_value(self, value):
        int_value = int(value)
        self.progress_bar.setValue(int_value)
        self.progress_label.setText(f"{int_value}%")

"""CustomLogger 신규 정의"""
class CustomLogWorker(QThread):
    update_label = pyqtSignal(str)
    log = ""

    def create_html(self, text):
        html = f'''
        <html>
        <head>
            <style>
                .normal_log {{
                    color: {PyQtAddon.get_color("content_text_color")};
                }}
            </style>
            <style>
                .error_log {{
                    color: {PyQtAddon.get_color("error_text_color")};
                }}
            </style>
        </head>
        <body>
            {text}
        </body>
        </html>
        '''

        return html

    def add_log(self, log):
        if self.log == "":
            self.log += '<span class="normal_log">'+'> '+log+'</span>'
        else:
            self.log += '<br/>'+'<span class="normal_log">'+'> '+log+'</span>'

        self.update_label.emit(self.create_html(self.log))

    def add_error_log(self, log):
        if self.log == "":
            self.log += '<span class="error_log">'+'> '+log+'</span>'
        else:
            self.log += '<br/>'+'<span class="error_log">'+'> '+log+'</span>'

        self.update_label.emit(self.create_html(self.log))

class CustomLogger(QWidget):
    def __init__(self):
        super().__init__()

        # QLabel 추가
        self.log_label = QLabel()
        self.log_label.setStyleSheet(f"""
                                     QLabel {{
                                         border:none;
                                         background-color:{PyQtAddon.get_color("background_color")};
                                         font-family:{PyQtAddon.text_font};
                                     }}
                                     """)
        
        # QScrollArea 생성 및 QLabel 추가
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.log_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
                                  /* ScrollArea 배경색 */
                                  QScrollArea {{
                                      border:none;
                                      background-color:{PyQtAddon.get_color("background_color")};  
                                  }}
                                  """
                                  +PyQtAddon.vertical_scrollbar_style
                                  +PyQtAddon.horizontal_scrollbar_style)
        
        # vertical scrollbar 조절을 위한 인스턴스 저장
        self.vertical_scrollbar = scroll_area.verticalScrollBar()

        # Layout 설정
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(scroll_area)

        # 메인스레드 동작 worker 생성
        self.worker = CustomLogWorker()
        self.worker.update_label.connect(self.update_label_text)
        self.worker.start()

    def update_label_text(self, text):
        self.log_label.setText(text)
        QTimer.singleShot(0, self.update_scrollbar)
        
    def update_scrollbar(self):
        self.vertical_scrollbar.setValue(self.vertical_scrollbar.maximum())
    
"""CustomControlButtons 신규 정의"""
class CustomControlButtons(QWidget):
    def __init__(self, next_button_callback):
        super().__init__()

        # Layout 설정
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # nex button 생성 후 layout 배치
        self.next_button = QPushButton()
        self.next_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.next_button.setFixedSize(40, 40)
        self.next_button.setStyleSheet(f"""
                                       QPushButton {{
                                        border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "next_step_button.svg"))}"); /* 기본 아이콘 */
                                       }}
                                       QPushButton:hover {{
                                        border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "next_step_button_hover.svg"))}"); /* hover 상태 아이콘 */
                                       }}
                                       QPushButton:pressed {{
                                        border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "next_step_button_pressed.svg"))}"); /* pressed 상태 아이콘 */
                                       }}
        """)
        self.next_button.clicked.connect(next_button_callback)
        layout.addWidget(self.next_button)
        
        self.setStyleSheet("QWidget { margin: 0px; padding: 0px; background-color: none;}")

"""CustomFileSystem 신규 정의 (QTreeView + CustomFileBrowser)"""
class CustomTreeView(QTreeView):
    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.callback = callback
                    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                self.callback(file_path)
                
        else:
            event.ignore()  

class CustomFileBorwser(QWidget):
    def __init__(self, on_path_changed):
        super().__init__()

        self.path = ""
        self.on_path_changed = on_path_changed
        self.setStyleSheet(f"""
                           QWidget {{
                             margin: 0px;
                             padding: 0px;
                             background-color: none;
                             border-top:1px solid {PyQtAddon.get_color("content_line_color")}; 
                             border-bottom:1px solid {PyQtAddon.get_color("content_line_color")};
                           }}
                           """)

        # Layout 생성
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 전체적인 border line 생성을 위한 QWidget 생성
        sub_widget = QWidget()
        sub_layout = QHBoxLayout()
        sub_widget.setLayout(sub_layout)
        main_layout.addWidget(sub_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Icon 생성
        svg_widget = QSvgWidget(PyQtAddon.convert_url(os.path.join(icons_directory, "current_directory_icon.svg")))
        svg_widget.setFixedSize(30, 30)
        svg_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        svg_widget.setStyleSheet("border:none")
        sub_layout.addWidget(svg_widget)

        # Directory showing label 생성
        self.directory_label = QLabel("...")
        self.directory_label.setStyleSheet(f"""
                                           color:{PyQtAddon.get_color("content_text_color")}; 
                                           font-family:'{PyQtAddon.text_font}'; 
                                           border:none;
                                           """)
        self.directory_label.setMinimumSize(0, 30)
        self.directory_label.setMaximumSize(16777215, 30)

        # QLabel의 크기 조정 정책 설정 (크기 제한을 없앰)
        self.directory_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        sub_layout.addWidget(self.directory_label)

        # Directory search button 생성
        directory_search_button = QPushButton()
        directory_search_button.setFixedSize(30, 30)
        directory_search_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        directory_search_button.clicked.connect(self.open_file_dialog)
        directory_search_button.setStyleSheet(f"""
                                              QPushButton {{
                                              border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "directory_search_icon.svg"))}"); /* 기본 아이콘 */
                                              }}
                                              QPushButton:hover {{
                                              border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "directory_search_icon_hover.svg"))}"); /* 기본 아이콘 */
                                              }}
                                              QPushButton:pressed {{
                                              border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "directory_search_icon_pressed.svg"))}"); /* 기본 아이콘 */
                                              }}
                                              """)
        sub_layout.addWidget(directory_search_button)
        sub_layout.setContentsMargins(0, 0, 0, 0)

        # QTimer를 사용하여 addDockWidget 이후 크기 확인
        QTimer.singleShot(0, self.check_label_width)

    def set_ellipsized_text(self, text):
        """QLabel의 텍스트가 너무 길면 ...으로 표시되도록 설정"""
        # QLabel의 폰트로 QFontMetrics 객체 생성
        metrics = QFontMetrics(self.directory_label.font())

        # QLabel의 너비에 맞춰 텍스트 자르기 (엘리시스 추가)
        elided_text = metrics.elidedText(text, Qt.ElideRight, self.directory_label.width())

        # 잘라낸 텍스트를 QLabel에 설정
        self.directory_label.setText(elided_text)

    def resizeEvent(self, event):
        """윈도우 크기가 조절되면 텍스트를 다시 자름"""
        self.set_ellipsized_text(self.path)
        super().resizeEvent(event)
    
    def set_directory(self, path):
        # label의 text만 변경
        self.path = path
        self.set_ellipsized_text(self.path)

    def check_label_width(self):
        """DockWidget 추가 이후 QLabel의 크기 확인"""
        self.set_ellipsized_text(self.path)

    def open_file_dialog(self):
        """파일 탐색기를 열어 사용자가 선택한 경로를 출력"""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")

        if directory:
            self.set_directory(directory)
            if self.on_path_changed:
                self.on_path_changed(self.path)
    
class CustomFileSystemWidget(QWidget):
    class CustomModel(QStandardItemModel):
        def __init__(self, directory):
            super().__init__()
            self.directory = directory
            
        def mimeData(self, indexes):
            mime_data = QMimeData()
            if indexes:
                # 드래그된 항목의 사용자 정의 "이름" 데이터를 MimeData에 저장
                item = self.itemFromIndex(indexes[0])

                # 파일 명 Text로 저장
                mime_data.setText(item.text())
                
                # 파일 경로 Url로 저장
                mime_data.setUrls([QUrl.fromLocalFile(os.path.join(self.directory, item.text()))])

            return mime_data
    
    def __init__(self, root_dir):
        super().__init__()

        # 현재 디렉토리 설정
        self.current_directory = root_dir

        # QFileSystemWatcher 설정 (파일 시스템 변화 감시)
        self.watcher = QFileSystemWatcher([self.current_directory])
        self.watcher.directoryChanged.connect(self.on_directory_changed)

        # QVBoxLayout 생성
        layout = QVBoxLayout()

        # File browser 생성
        self.file_browser = CustomFileBorwser(self.on_path_changed)
        layout.addWidget(self.file_browser)

        # QStandardItemModel 생성
        self.model = self.CustomModel(self.current_directory)
        self.model.setHorizontalHeaderLabels(['Files and Folders'])

        # 파일 및 폴더 추가
        self.add_items(self.model, self.current_directory)

        # QTreeView 생성
        self.tree = CustomTreeView(self.on_drag_and_drop_event)
        self.tree.setModel(self.model)
        self.tree.setItemsExpandable(False)  # 항목 확장 불가
        self.tree.setRootIsDecorated(False)  # 트리 루트 장식 없애기

        # 헤더 숨기기 (열 이름 숨기기)
        self.tree.setHeaderHidden(True)
        
        # 파일명만 보이도록 다른 열 숨기기 (파일 이름은 0번 열)
        self.tree.setColumnHidden(1, True)  # 파일 크기 숨기기
        self.tree.setColumnHidden(2, True)  # 파일 종류 숨기기
        self.tree.setColumnHidden(3, True)  # 수정 날짜 숨기기

        # 드래그 앤 드롭 설정
        self.tree.setAcceptDrops(True)
        self.tree.setDragEnabled(True)
        self.tree.setDropIndicatorShown(True)

        # QTreeView에서 더블 클릭 시 항목을 처리
        self.tree.doubleClicked.connect(self.on_item_double_clicked)

        self.tree.setStyleSheet(f"""
                                QTreeView {{
                                    background-color: {PyQtAddon.get_color("background_color")};  /* 배경색 검정 */
                                    color: {PyQtAddon.get_color("title_text_color")};
                                    font-family:{PyQtAddon.text_font};
                                    border:none;
                                }}
                                QTreeView::item {{
                                    background-color: {PyQtAddon.get_color("background_color")};  /* 각 항목의 배경색 검정 */
                                    color: {PyQtAddon.get_color("content_text_color")};  /* 각 항목의 텍스트 색상 흰색 */
                                    font-family:{PyQtAddon.text_font};
                                }}
                                QTreeView::item:hover {{
                                    background-color: {PyQtAddon.get_color("content_hover_color")};
                                }}
                                QTreeView::item:selected {{
                                    background-color: {PyQtAddon.get_color("content_hover_color")};
                                }}
                                """
                                +PyQtAddon.vertical_scrollbar_style
                                +PyQtAddon.horizontal_scrollbar_style)

        # QVBoxLayout에 QTreeView 추가
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.setStyleSheet("QWidget { margin: 0px; padding: 0px; background-color: none;}")

    def add_items(self, parent_item, directory):
        # 파일 브라우져의 경로 수정 
        self.file_browser.set_directory(self.current_directory)
        
        # 모델의 경로 수정
        self.model.directory = self.current_directory

        """특정 디렉토리의 파일 및 폴더를 트리 뷰에 추가"""
        # 상위 디렉토리 경로 계산
        parent_directory = os.path.abspath(os.path.join(self.current_directory, ".."))

        # 상위 디렉토리가 존재할 경우 .. 항목 추가
        if os.path.isdir(parent_directory) and parent_directory != "C:\\":
            # 가장 위에 .. 항목 추가 (상위 디렉토리 이동)
            parent_directory_selector = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "folder_directory_icon.svg"))), '..')
            parent_directory_selector.setEditable(False)
            parent_item.appendRow(parent_directory_selector)

        # 디렉토리 목록과 파일 목록을 분리
        folders = []
        files = []
        for item_name in sorted(os.listdir(directory)):
            item_path = os.path.join(directory, item_name)
            if os.path.isdir(item_path):
                folders.append(item_name)
            else:
                files.append(item_name)

        # 폴더부터 먼저 추가
        for folder in folders:
            folder_item = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "folder_icon.svg"))), folder)
            folder_item.setEditable(False)
            parent_item.appendRow(folder_item)

        # 파일을 나중에 추가
        for file in files:
            if file.endswith('.csv'):
                file_item = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "file_csv_icon.svg"))), file)
            else:
                file_item = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "file_normal_icon.svg"))), file)
            file_item.setEditable(False)
            parent_item.appendRow(file_item)

    def on_item_double_clicked(self, index):
        """더블 클릭 시 .. 항목을 처리하여 상위 디렉토리로 이동"""
        selected_item = self.model.itemFromIndex(index)
        if selected_item.text() == '..':
            # 상위 디렉토리 경로 계산
            parent_directory = os.path.abspath(os.path.join(self.current_directory, ".."))

            # 상위 디렉토리가 존재하는지 확인
            if os.path.isdir(parent_directory):
                # 상위 디렉토리로 이동
                self.current_directory = parent_directory
                self.model.clear()  # 모델을 초기화
                self.add_items(self.model, self.current_directory)  # 상위 디렉토리 내용 추가)

        else:
            # 선택된 디렉토리로 이동
            clicked_path = os.path.join(self.current_directory, selected_item.text())
            if os.path.isdir(clicked_path):
                self.current_directory = clicked_path
                self.model.clear()  # 모델을 초기화
                self.add_items(self.model, self.current_directory)  # 새로운 디렉토리 내용 추가

        # QFileSystemWatcher에 새로운 경로 등록
        self.watcher.removePaths(self.watcher.directories())  # 이전 경로 제거
        self.watcher.addPath(self.current_directory)  # 새 경로 추가

    def on_directory_changed(self, path):
        """감시 중인 디렉토리에서 변경이 발생할 때 호출"""
        self.model.clear()  # 모델을 초기화
        self.add_items(self.model, self.current_directory)  # 현재 디렉토리 내용 업데이트

    def on_drag_and_drop_event(self, file_path):
        # 드랍된 파일의 상위 경로 추출
        parent_directory = os.path.abspath(os.path.join(file_path, ".."))
        self.current_directory = parent_directory
        self.model.clear()  # 모델을 초기화
        self.add_items(self.model, self.current_directory)  # 현재 디렉토리 내용 업데이트

    def on_path_changed(self, file_path):
        self.current_directory = file_path
        self.model.clear()
        self.add_items(self.model, self.current_directory)

"""위젯 재정의"""
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
        
# QMessageBox
class CustomMessageBox(QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 스타일 시트 설정 (여기서 QMessageBox에 대한 스타일을 적용)
        self.setStyleSheet(f"""
            QMessageBox {{
                background-color:{PyQtAddon.get_color("background_color")};
                border:none;
            }}
            QLabel {{
                border:none;
            }}
            QMessageBox QPushButton {{
                background-color:{PyQtAddon.get_color("point_color_1")};
                color:{PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border-radius: 0px;
                border:none;
            }}
            QMessageBox QPushButton:hover {{
                background-color:{PyQtAddon.get_color("point_color_2")};
                border:none;
            }}
        """)

    @staticmethod
    def information(parent, title, text):
        # 기본 QMessageBox.warning() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)

        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)

        # 경고 아이콘 설정
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()
    
    @staticmethod
    def question(parent, title, text, setStandardButtons, setDefaultButton):
        # 기본 QMessageBox.question() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)

        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)

        # 질문 아이콘 설정
        msg_box.setIcon(QMessageBox.Question)
        
        # Standarad 버튼 설정
        msg_box.setStandardButtons(setStandardButtons)
        
        # 기본 선택 설정
        msg_box.setDefaultButton(setDefaultButton)

        # 사용자의 응답 반환
        return msg_box.exec_()

    @staticmethod
    def warning(parent, title, text):
        # 기본 QMessageBox.warning() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)

        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)

        # 경고 아이콘 설정
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()

    @staticmethod
    def critical(parent, title, text):
        # 기본 QMessageBox.critical() 기능을 재정의하여 스타일이 적용된 메시지 박스 생성
        msg_box = CustomMessageBox(parent)
        msg_box.setWindowTitle(title)
        
        # 텍스트에 스타일 적용 (색상과 폰트 크기 변경)
        styled_text = f'<span style="color:{PyQtAddon.get_color("title_text_color")}; font-family:{PyQtAddon.text_font};">{text}</span>'
        msg_box.setText(styled_text)
        
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()
    
# QInputDialog
class CustomInputDialog(QInputDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # QInputDialog에 대한 스타일 시트 적용
        self.setStyleSheet(f"""
            QInputDialog {{
                background-color: {PyQtAddon.get_color("background_color")};
                border: none;
            }}
            QLabel {{
                color: {PyQtAddon.get_color("title_text_color")};
                font-family: {PyQtAddon.text_font};
                border: none;
            }}
            QLineEdit {{
                background-color: {PyQtAddon.get_color("point_color_1")};
                color: {PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border: 1px solid {PyQtAddon.get_color("line_color")};
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: {PyQtAddon.get_color("point_color_1")};
                color: {PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border-radius: 0px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {PyQtAddon.get_color("point_color_2")};
                border: none;
            }}
        """)

    @staticmethod
    def getText(parent, title, label, text=""):
        # CustomInputDialog 사용하여 텍스트 입력 다이얼로그 표시
        dialog = CustomInputDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setTextValue(text)
        dialog.setInputMode(QInputDialog.TextInput)

        # 입력된 텍스트 및 결과 반환
        if dialog.exec_() == QInputDialog.Accepted:
            return dialog.textValue(), True
        else:
            return "", False

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 레이아웃 생성
        self.setWindowTitle("Please Wait")
        # self.setFixedSize(300, 100)
        self.setModal(True) # 부모 창과 상호 작용 차단
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)  # 닫기 버튼 비활성화

        # 레이아웃 설정
        layout = QVBoxLayout()

        # Progress bar 생성
        # self.progress_bar = QProgressBar()
        self.progress_bar = CustomProgressBar(0, parent=self)
        # self.progress_bar.setAlignment(Qt.AlignCenter)
        # self.progress_bar.setRange(0, 100)

        # "작업 중" 애니메이션 GIF 추가
        self.loading_label = QLabel(self)
        self.movie = QMovie(PyQtAddon.convert_url(os.path.join(icons_directory, "loading_icon.gif")))  # 로딩 애니메이션 GIF 파일 경로
        self.movie.setScaledSize(QSize(40, 40)) # QMovie의 크기를 특정 픽셀 크기로 설정
        self.loading_label.setMovie(self.movie)
        self.movie.start()

        # 정보 라벨 추가
        self.info_label = QLabel("The task is in progress. Please wait...", self)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(f"""QLabel {{
                                         background-color: {PyQtAddon.get_color("background_color")};
                                         color: {PyQtAddon.get_color("title_text_color")};
                                         }}""")
        
        # 레이아웃에 위젯 추가
        layout.addWidget(self.loading_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.info_label)

        self.setLayout(layout)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {PyQtAddon.get_color("background_color")};
                border: none;
            }}
        """)

    def start_progress(self):
        """백그라운드 스레드 작업 시작"""
        self.progress_bar.set_value(0)  # ProgressBar 초기화
        self.show()

    def update_progress(self, value):
        """진행 상황을 업데이트"""
        self.progress_bar.set_value(int(value))

    def stop_progress(self):
        self.progress_bar.set_value(100)
        self.accept()

# QDialog
class CustomLoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        self.setModal(True) # 부모 창과 상호 작용 차단
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)  # 닫기 버튼 비활성화

        # 레이아웃 생성
        layout = QVBoxLayout()

        # "작업 중" 애니메이션 GIF 추가
        self.loading_label = QLabel(self)
        self.movie = QMovie(PyQtAddon.convert_url(os.path.join(icons_directory, "loading_icon.gif")))  # 로딩 애니메이션 GIF 파일 경로
        self.movie.setScaledSize(QSize(40, 40)) # QMovie의 크기를 특정 픽셀 크기로 설정
        self.loading_label.setMovie(self.movie)
        self.movie.start()
        
        # 정보 라벨 추가
        self.info_label = QLabel("The task is in progress. Please wait...", self)
        self.info_label.setAlignment(Qt.AlignCenter)

        # 텍스트 스타일 설정
        self.info_label.setStyleSheet(f"""QLabel {{
                                         background-color: {PyQtAddon.get_color("background_color")};
                                         color: {PyQtAddon.get_color("title_text_color")};
                                         font-family: {PyQtAddon.text_font};
                                         }}""")

        # 레이아웃에 위젯 추가
        layout.addWidget(self.loading_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.setLayout(layout)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {PyQtAddon.get_color("background_color")};
                border: none;
            }}
        """)

    def on_task_started(self):
        self.show()

    def on_task_finished(self):
        # 작업 완료 시 로딩 대화상자 닫기
        self.accept()

# QDockWidget
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
            
# QMainWindow
class CustomMainWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()

        # close 이벤트 등록
        self.on_closed_callback_list = []

        # 메인 중앙 위젯 설정
        self.central_widget = QFrame(self)
        self.setCentralWidget(self.central_widget)

        # 아이콘 설정
        self.setWindowIcon(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "program_icon.svg"))))

        # 메인 윈도우 설정
        self.setGeometry(0, 0, PyQtAddon.main_window_width, PyQtAddon.main_window_height)
        self.setWindowTitle(title)
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

"""위젯 신규 정의"""
# NoDataWidget 신규 정의
class CustomNoDataWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(icons_directory, 'nodata.ui'), self)

        # Layout 설정
        layout = self.findChild(QVBoxLayout, "layout")
        self.setLayout(layout)
        # SVG widget 추가
        svg_widget = QSvgWidget(PyQtAddon.convert_url(os.path.join(icons_directory, "no_data_icon.svg")))
        svg_widget.setFixedSize(60, 80)
        layout.addWidget(svg_widget, alignment=Qt.AlignCenter)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QWidget { margin: 0px; padding: 0px; background-color: none;}")
        
# CustomGridKeyword 위젯 상속을 위한 부모 클래스
class CustomGridKeywordWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 키워드를 격자 형태로 배치하기 위해 GridLayout 생성
        self.grid_layout = QGridLayout()

        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        # 마지막으로 클릭된 라벨을 추적 (Single click에서 사용)
        self.last_clicked_label = None  

        # 현재 클릭되어 있는 모든 라벨을 추적 (Multi click에서 사용)
        self.selected_keywords = []

        # 이벤트 콜백
        self.on_clicked = None

        # 레이아웃 설정
        self.setLayout(self.grid_layout)

        # label의 최소 width 및 height 설정 
        self.column_width = 25
        self.column_height = 25

        # 키워드 저장
        self.keywords = None
        self.labels = []

        # 과도한 업데이트 방지
        self.is_updating = False

    def calculate_minimum_height(self):
        """라벨의 최소 높이를 기반으로 창의 최소 높이 계산"""
        if self.keywords is None:
            return
        
        columns = max(1, self.width() // self.column_width)
        print(columns)
        rows = (len(self.keywords) + columns - 1) // columns  # 키워드 수에 따른 행 개수 계산
        return rows *  self.column_height + (rows - 1) * 0  # 라벨 높이와 행 간격을 고려하여 최소 높이 계산
        # rows = (len(self.keywords) + columns - 1) // columns  # 키워드 수에 따른 행 개수 계산
        # return rows *  self.column_height + (rows - 1) * 0  # 라벨 높이와 행 간격을 고려하여 최소 높이 계산

    def resizeEvent(self, event):
        """윈도우 크기가 변경될 때 호출"""
        self.update_layout()
        super().resizeEvent(event)

    def update_layout(self):
        """현재 창 크기에 따라 키워드 레이아웃 업데이트"""
        if self.keywords is None:
            return
        
        if len(self.labels) == 0:
            return
        
        if self.is_updating:
            return
        
        self.is_updating = True

        # 기존 레이아웃 초기화
        self.clear_layout()

        # 창의 폭을 기준으로 열의 개수 계산
        widget_width = self.width()
        columns = max(1, widget_width // self.column_width)

        # 키워드 추가
        for i, label in enumerate(self.labels):
            row = i // columns
            col = i % columns
            self.grid_layout.addWidget(label, row, col)

        # 창의 최소 크기 업데이트
        self.setMinimumSize(0, self.calculate_minimum_height())

        self.is_updating = False

    def clear(self):
        """QGridLayout 비우기"""
        self.keywords = None
        self.selected_keywords.clear()
        self.last_clicked_label = None
        self.labels.clear()
        self.clear_layout()

    def clear_layout(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # 레이아웃에서 위젯 제거 (삭제하지 않음)
                self.grid_layout.removeWidget(widget)

# CustomGridKeywordMultiClickWidget : 주어진 keyword를 grid로 배치하고, 선택 할 수 있는 위젯
# (한 번의 클릭으로 선택, 여러 항목 선택 가능)
class CustomGridKeywordMultiClickkWidget(CustomGridKeywordWidget):
    class CustomGridKeywordLabel(QLabel):
        def __init__(self, keyword, parent=None):
            super().__init__(keyword, parent)
            self.keyword = keyword

            # 기본 스타일 설정
            self.default_style = f"""
            background-color: {PyQtAddon.get_color("background_color")};
            color: {PyQtAddon.get_color("content_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """
            self.hover_style   = f"""
            background-color: {PyQtAddon.get_color("point_color_1")};
            color: {PyQtAddon.get_color("content_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """
            self.clicked_style = f"""
            background-color: {PyQtAddon.get_color("point_color_5")};
            color: {PyQtAddon.get_color("title_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """

            self.setStyleSheet(self.default_style)

            # 텍스트 중앙 정렬
            self.setAlignment(Qt.AlignCenter)

            # 최소 및 최대 높이 설정
            self.setMinimumHeight(25)  # 최소 높이 (픽셀 단위로 설정)
            self.setMaximumHeight(50)  # 최대 높이 (픽셀 단위로 설정)

        def mousePressEvent(self, event):
            """클릭 이벤트 처리"""
            if event.button() == Qt.LeftButton:
                # 이미 선택 되어 있는 경우
                if self.keyword in self.parentWidget().selected_keywords:
                    self.setStyleSheet(self.default_style)  # 클릭된 스타일로 변경
                    self.parentWidget().selected_keywords.remove(self.keyword)
                    
                # 선택 되어 있지 않은 경우
                else:
                    self.setStyleSheet(self.clicked_style)  # 클릭된 스타일로 변경
                    self.parentWidget().selected_keywords.append(self.keyword)

                if self.parentWidget().on_clicked:
                    self.parentWidget().on_clicked(self.parentWidget().selected_keywords)

        def enterEvent(self, event):
            """마우스가 라벨 위로 올라왔을 때 배경색 변경"""
            self.setStyleSheet(self.hover_style)

        def leaveEvent(self, event):
            """마우스가 라벨 위에서 벗어났을 때 배경색 되돌리기"""
            if self.keyword in self.parentWidget().selected_keywords:
                self.setStyleSheet(self.clicked_style)
            else:
                self.setStyleSheet(self.default_style)

    def __init__(self, parent=None):
        super().__init__(parent)

    def set_keywords(self, keywords):
        self.labels.clear()
        self.keywords = keywords
        for i, keyword in enumerate(self.keywords):
            self.labels.append(self.CustomGridKeywordLabel(keyword, self))
        self.update_layout()
 
# CustomGridKeywordWidget : 주어진 keyword를 grid로 배치하고, 선택 할 수 있는 위젯
# (더블 클릭으로 선택, 한 항목만 선택 가능)
class CustomGridKeywordSingleClickWidget(CustomGridKeywordWidget):
    class CustomGridKeywordLabel(QLabel):
        def __init__(self, keyword, parent=None):
            super().__init__(keyword, parent)
            self.keyword = keyword

            # 기본 스타일 설정
            self.default_style = f"""
            background-color: {PyQtAddon.get_color("background_color")};
            color: {PyQtAddon.get_color("content_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """
            self.hover_style   = f"""
            background-color: {PyQtAddon.get_color("point_color_1")};
            color: {PyQtAddon.get_color("content_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """
            self.clicked_style = f"""
            background-color: {PyQtAddon.get_color("point_color_5")};
            color: {PyQtAddon.get_color("title_text_color")};
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 3px;
            padding-bottom: 3px;
            """

            self.setStyleSheet(self.default_style)

            # 텍스트 중앙 정렬
            self.setAlignment(Qt.AlignCenter)

            # 최소 및 최대 높이 설정
            self.setMinimumHeight(25)  # 최소 높이 (픽셀 단위로 설정)
            self.setMaximumHeight(50)  # 최대 높이 (픽셀 단위로 설정)
                    
        def mouseDoubleClickEvent(self, event):
            """더블 클릭 이벤트 처리"""
            if event.button() == Qt.LeftButton:
                # 이전과 다른 라벨이 선택된 경우
                if self.parentWidget().last_clicked_label != self:
                    self.parentWidget().reset_previous_click()  # 이전 클릭된 라벨 초기화
                    self.setStyleSheet(self.clicked_style)  # 클릭된 스타일로 변경
                    self.parentWidget().last_clicked_label = self  # 현재 라벨을 기록

                    # 더블 클릭된 키워드 출력
                    if self.parentWidget().on_clicked is not None:
                        self.parentWidget().on_clicked(self.keyword)

                # 이전과 같은 라벨이 선택된 경우
                else:
                    self.parentWidget().reset_previous_click()
                    if self.parentWidget().on_clicked is not None:
                        self.parentWidget().on_clicked(None)

        def enterEvent(self, event):
            """마우스가 라벨 위로 올라왔을 때 배경색 변경"""
            self.setStyleSheet(self.hover_style)

        def leaveEvent(self, event):
            """마우스가 라벨 위에서 벗어났을 때 배경색 되돌리기"""
            if self != self.parentWidget().last_clicked_label:
                self.setStyleSheet(self.default_style)
            else:
                self.setStyleSheet(self.clicked_style)

    def __init__(self, parent=None):
        super().__init__(parent)
        
    def set_keywords(self, keywords):
        self.labels.clear()
        self.keywords = keywords
        for i, keyword in enumerate(self.keywords):
            self.labels.append(self.CustomGridKeywordLabel(keyword, self))
        self.update_layout()

    def reset_previous_click(self):
        """이전에 더블 클릭된 라벨을 기본 스타일로 되돌림"""
        if self.last_clicked_label:
            self.last_clicked_label.setStyleSheet(self.last_clicked_label.default_style)
            self.last_clicked_label = None
                      
class CustomComboBoxDialog(QDialog):
    def __init__(self, default_options=None, parent=None):
        """Data name, type, state 선택할 수 있는 combo box 세 개를 가진 QDialog

        Args:
            default_options (str list): 각 콤보 박스의 기본값. Defaults to None.
        """
        
        # 각 콤보 박스 옵션 설정
        data_name_list = ["AA", "FE", "ML", "CB1", "CB2", "CB3", "VALID", "TEST"]
        data_type_list = ["marker", "sensor"]
        data_state_list = ["raw", "refined"]
        
        # default_index 유효성 검사
        if default_options is None:
            default_index = [0, 0, 0]
        else:
            if len(default_options) != 3:
                default_index = [0, 0, 0]
                
            else:
                default_index = [
                    data_name_list. index(default_options[0]) if default_options[0] in data_name_list  else 0,
                    data_type_list. index(default_options[1]) if default_options[1] in data_type_list  else 0,
                    data_state_list.index(default_options[2]) if default_options[2] in data_state_list else 0
                ]
            
        super().__init__(parent)
        self.setWindowTitle("Select Options")

        # 레이아웃 설정
        layout = QVBoxLayout(self)

        # Data name dropdown
        self.data_name_combo = CustomComboBox(self)
        self.data_name_combo.addItems(data_name_list)
        layout.addWidget(QLabel("Select data name:"))
        layout.addWidget(self.data_name_combo)
        layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.data_name_combo.setCurrentIndex(default_index[0])

        # Data type dropdown
        self.data_type_combo = CustomComboBox(self)
        self.data_type_combo.addItems(data_type_list)
        layout.addWidget(QLabel("Select data type:"))
        layout.addWidget(self.data_type_combo)
        layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.data_type_combo.setCurrentIndex(default_index[1])

        # Data state dropdown
        self.data_state_combo = CustomComboBox(self)
        self.data_state_combo.addItems(data_state_list)
        layout.addWidget(QLabel("Select data state:"))
        layout.addWidget(self.data_state_combo)
        layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.data_state_combo.setCurrentIndex(default_index[2])

        # OK, Cancel 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {PyQtAddon.get_color("background_color")};
                border: none;
            }}
            QLabel {{
                color: {PyQtAddon.get_color("title_text_color")};
                font-family: {PyQtAddon.text_font};
                border: none;
            }}
            QPushButton {{
                background-color: {PyQtAddon.get_color("point_color_1")};
                color: {PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border-radius: 0px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {PyQtAddon.get_color("point_color_2")};
                border: none;
            }}
        """)

    def get_selections(self):
        """선택된 항목을 반환

        Returns:
            str list: [data name, data type, data state]
        """
        # 선택된 항목을 반환
        return [self.data_name_combo.currentText(), self.data_type_combo.currentText(), self.data_state_combo.currentText()]
    
    