from .base import *
from .ui_common import *

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
                             QTabWidget, QSlider)
                      
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
# check_and_install_oxanium_font()

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
    main_window_width = 800
    main_window_height = 600
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
    