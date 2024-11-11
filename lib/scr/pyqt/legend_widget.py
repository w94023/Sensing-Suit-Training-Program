from .common import *
from .adjustable_grid_layout import *

class CustomLegendWidget(QWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(self.parent)

        # widget의 크기에 따라 크기를 적절히 조절하는 grid layout 생성
        self.grid_widget = AdjustableGridLayout(minimum_grid_width=100, minimum_grid_height=25, parent=self.parent)
        self.grid_widget.enable_minimum_size_clamping(False)
        self.grid_layout = self.grid_widget.get_layout()
        
        # main layout 생성 및 grid_widget 배치
        layout = QVBoxLayout()
        layout.addWidget(self.grid_widget)
        layout.setContentsMargins(80, 10, 80, 10)
        
        # main layout 배치
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
    def clear_layout(self):
        self.grid_widget.clear()
                
    def set_legend(self, handles, labels):
        # grid layout에 배치될 아이템 생성
        grid_items = []
        for i in range(len(labels)):
            # tuple_color = handles[i].get_color()
            r, g, b, a = handles[i].get_color()
            grid_items.append(self.create_legend_item(labels[i], QColor(int(r*255), int(g*255), int(b*255), int(a*255))))
        
        # grid item 설정
        self.grid_widget.set_items(grid_items)

    def create_legend_item(self, label_text, color):
        # 레이아웃 생성 (아이콘 + 텍스트)
        legend_item_layout = QHBoxLayout()

        # 색상 박스 아이콘 생성
        color_label = QLabel(self)
        pixmap = QPixmap(20, 2)
        pixmap.fill(color)  # 주어진 색상으로 박스를 채움
        color_label.setPixmap(pixmap)

        # 텍스트 라벨 생성
        text_label = QLabel(label_text)
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        text_label.setStyleSheet(f"""background-color:{UiStyle.get_color("background_color")};
                                     color:{UiStyle.get_color("content_text_color")}""")

        # 레이아웃에 아이콘과 텍스트 추가
        legend_item_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        legend_item_layout.addWidget(color_label)
        legend_item_layout.addWidget(text_label)
        legend_item_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        legend_item_layout.setContentsMargins(0, 0, 0, 0)

        return legend_item_layout