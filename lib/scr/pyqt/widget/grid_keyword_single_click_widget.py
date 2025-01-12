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
                
class CustomGridKeywordSingleClickWidget(CustomGridKeywordWidget):
    # CustomGridKeywordWidget : 주어진 keyword를 grid로 배치하고, 선택 할 수 있는 위젯
    # (더블 클릭으로 선택, 한 항목만 선택 가능)

    def __init__(self, parent=None):
        super().__init__(parent)
        
    def set_keywords(self, keywords):
        self.labels.clear()
        self.keywords = keywords
        for i, keyword in enumerate(self.keywords):
            self.labels.append(CustomGridKeywordLabel(keyword, self))
        self.update_layout()

    def reset_previous_click(self):
        """이전에 더블 클릭된 라벨을 기본 스타일로 되돌림"""
        if self.last_clicked_label:
            self.last_clicked_label.setStyleSheet(self.last_clicked_label.default_style)
            self.last_clicked_label = None
                    