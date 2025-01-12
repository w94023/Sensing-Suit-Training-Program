from ....pyqt_base import *
from ....ui_common import *

tree_view_button_style = f"""
                          QPushButton {{
                              background-color:transparent;
                              border:none;
                          }}
                          QPushButton:hover {{
                              background-color:{UiStyle.get_color("point_color_1")}
                          }}
                          QPushButton:pressed {{
                              background-color:{UiStyle.get_color("point_color_1")}
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