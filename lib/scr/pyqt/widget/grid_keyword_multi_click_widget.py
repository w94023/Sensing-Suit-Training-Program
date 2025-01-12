from ....pyqt_base import *
from ....ui_common import *

from .grid_keyword_widget import *

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
                
class CustomGridKeywordMultiClickkWidget(CustomGridKeywordWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def set_keywords(self, keywords):
        self.labels.clear()
        self.keywords = keywords
        for i, keyword in enumerate(self.keywords):
            self.labels.append(CustomGridKeywordLabel(keyword, self))
        self.update_layout()