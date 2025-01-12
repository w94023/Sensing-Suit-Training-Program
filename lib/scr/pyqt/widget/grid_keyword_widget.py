from ....pyqt_base import *
from ....ui_common import *

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