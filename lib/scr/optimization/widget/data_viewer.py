from ..common import *
from .common import *

class OptimizationResultFileDataViewer(QWidget):                 
    def __init__(self, parent=None):        
        self.parent = parent
        super().__init__(self.parent)
        
        # # JSON data manager 저장 및 이벤트 연결
        # self.json_data_manager = json_data_manager
        # self.json_data_manager.on_target_file_changed += self.__update_list
        
        # UI 초기화
        self.__init_ui()
        
        # 이벤트 생성
        self.on_item_clicked = CustomEventHandler()
        self.on_item_double_clicked = CustomEventHandler()

        # # 이벤트 연결
        # self.csv_data_tree_view.on_item_clicked += self.on_item_clicked
        # self.csv_data_tree_view.on_item_double_clicked += self.on_item_double_clicked

    def __init_ui(self):
        # 레이아웃 설정
        layout = QVBoxLayout()
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

        # 현재 선택된 파일 표시
        # Layout 생성
        label_layout = QHBoxLayout()
        label_layout.setContentsMargins(0, 2, 0, 2)
        label_widget = QWidget()
        label_widget.setLayout(label_layout)
        label_widget.setStyleSheet(f"""
                                    border-top:1px solid {UiStyle.get_color("content_line_color")};
                                    border-bottom:1px solid {UiStyle.get_color("content_line_color")};
                                    """)

        # Icon 생성
        label_layout.addWidget(PyQtAddon.create_svg_widget("target_icon.svg", 30, 30))

        self.selected_file_label = QLabel(self.parent)
        self.selected_file_label.setStyleSheet(f"""
                                               background-color: {UiStyle.get_color("background_color")};
                                               color: {UiStyle.get_color("content_text_color")};
                                               border: none;
                                               """)
        label_layout.addWidget(self.selected_file_label)
        content_layout.addWidget(label_widget)


        # data tree view 생성
        self.csv_data_tree_view = CustomDataTreeView(["", "Name", "Type", "State"], None, self.parent)
        self.csv_data_tree_view.enable_first_column_as_icon(True)
        content_layout.addWidget(self.csv_data_tree_view)

        # - 버튼 생성 (파일 삭제)
        self.remove_button = QPushButton()
        # self.remove_button.clicked.connect(self.csv_data_tree_view.remove_data)
        self.remove_button.setFixedSize(20, 20)
        PyQtAddon.set_button_icon(self.remove_button, "minus_button_icon.svg", 20, 20)
        self.remove_button.setStyleSheet(f"""
                                      QPushButton {{
                                          background-color:transparent;
                                          border:none;
                                      }}
                                      QPushButton:hover {{
                                          background-color:{UiStyle.get_color("point_color_1")}
                                      }}
                                      QPushButton:pressed {{
                                          background-color:{UiStyle.get_color("point_color_2")}
                                      }}
                                      """)
        
        # 버튼을 오른쪽으로 정렬시키기 위한 spacer 추가
        spacer = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # 버튼 레이아웃 설정
        button_layout = QHBoxLayout()
        button_layout.addItem(spacer)
        button_layout.addWidget(self.remove_button)
        content_layout.addLayout(button_layout)