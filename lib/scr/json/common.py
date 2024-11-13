from ...pyqt_base import *
from ...ui_common import *
from ..pyqt import *
from ..csv import *
from ..thread import*

root_directory =  os.path.dirname( # 상위 디렉토리 (root)
                     os.path.dirname( # 상위 디렉토리 (lib)
                         os.path.dirname( # 상위 디렉토리 (scr)
                             os.path.dirname(os.path.abspath(__file__))))) # 현재 파일 디렉토리 (json)

json_directory = os.path.join(root_directory, 'data')

tree_view_button_style = f"""
                          QPushButton {{
                              background-color:transparent;
                              border:none;
                          }}
                          QPushButton:hover {{
                              background-color:{PyQtAddon.get_color("point_color_1")}
                          }}
                          QPushButton:pressed {{
                              background-color:{PyQtAddon.get_color("point_color_1")}
                          }}
                          """

def create_tree_view_button(icon_name, width, height, callback=None):
    """주어진 icon으로 TreeView 스타일의 버튼 위젯 생성하는 메서드

    Args:
        icon_name (str): icon_directory에 존재하는 파일 명
        width (int): 넓이 픽셀
        height (int): 높이 픽셀
        callback (method): 버튼에 연결할 콜백. Default to None

    Returns:
        QButtonWidget: TreeView 스타일 버튼 위젯
    """
    
    tree_view_button = QPushButton()
    
    # 버튼 콜백 연결
    if callback is not None:
        tree_view_button.clicked.connect(callback)
    
    # 버튼 아이콘 설정
    PyQtAddon.set_button_icon(tree_view_button, icon_name, width, height)
    
    # 버튼 크기 설정
    tree_view_button.setFixedSize(width, height)
    
    # 버튼 스타일 설정
    tree_view_button.setStyleSheet(tree_view_button_style)
    
    return tree_view_button

class IconRightDelegate(QStyledItemDelegate):
    """아이콘을 항목의 오른쪽 끝에 배치하는 델리게이트"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Icon 로드
        self.saved_json_data_icon   = PyQtAddon.create_svg_icon("saved_json_data_icon.svg", 16, 16)
        self.unsaved_json_data_icon = PyQtAddon.create_svg_icon("unsaved_json_data_icon.svg", 16, 16)
        
    def paint(self, painter, option, index):
        # 아이콘을 오른쪽으로 이동시켜서 다시 렌더링
        option.decorationPosition = QStyleOptionViewItem.Right  # 기본 아이콘 렌더링 방지
        QStyledItemDelegate.paint(self, painter, option, index)