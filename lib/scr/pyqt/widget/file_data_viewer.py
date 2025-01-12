from ....pyqt_base import *
from ....ui_common import *

from .tree_view import *

target_filename_extension = '.h5'

class FileDataViewer(QWidget):
    def __init__(self, tree_view, parent=None):
        self.parent = parent
        super().__init__(self.parent)
        
        # 이벤트 생성
        self.on_item_clicked = CustomEventHandler()
        self.on_item_double_clicked = CustomEventHandler()
        self.on_data_remove_requested = CustomEventHandler()
        
        # UI 초기화
        self.__init_ui(tree_view)

        # 인스턴스 데이터
        self.selected_item_by_double_click = None
        self.selected_items_by_click = None

        # 이벤트 연결
        self.tree_view.on_item_clicked += self.__on_item_clicked
        self.tree_view.on_item_clicked += self.on_item_clicked
        self.tree_view.on_item_double_clicked += self.__on_item_double_clicked
        self.tree_view.on_item_double_clicked += self.on_item_double_clicked
        
    def __init_ui(self, tree_view):
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
        self.tree_view = tree_view
        content_layout.addWidget(self.tree_view)

        # - 버튼 생성 (파일 삭제)
        self.remove_button = QPushButton()
        self.remove_button.clicked.connect(self.__on_data_remove_requested)
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

    def __on_item_clicked(self, selected_items):
        if selected_items is None:
            self.selected_items_by_click = None
            return
        
        if len(selected_items) == 0:
            self.selected_items_by_click = None
            return
        
        self.selected_items_by_click = []
        for selected_item in selected_items:
            self.selected_items_by_click.append('-'.join(selected_item))

    def __on_item_double_clicked(self, selected_item):
        if selected_item is None:
            self.selected_item_by_double_click = None
            return
        
        if len(selected_item) != 3:
            self.selected_item_by_double_click = None
            return
        
        self.selected_item_by_double_click = []
        self.selected_item_by_double_click.append('-'.join(selected_item))

    def __on_data_remove_requested(self):
        # 클릭으로 선택된 아이템이 없을 경우
        target_item_list = []
        if self.selected_items_by_click is None:

            # 더블 클릭으로 선택된 아이템이 없을 경우, 빈 list 반환하고 종료
            if self.selected_item_by_double_click is None:
                self.__remove_data_list(target_item_list)
                return
            
            # 더블 클릭으로 선택된 아이템이 있을 경우, 더블 클릭으로 선택된 아이템 반환하고 종료
            else:
                self.__remove_data_list(self.selected_item_by_double_click)
                return
            
        # 클릭으로 선택된 아이템이 있을 경우
        else:
            for item in self.selected_items_by_click:
                target_item_list.append(item)

            # 더블 클릭으로 선택된 아이템도 포함시킴
            if self.selected_item_by_double_click is not None:
                if self.selected_item_by_double_click[0] not in target_item_list:
                    target_item_list.append(self.selected_item_by_double_click[0])

            self.__remove_data_list(target_item_list)

    def __remove_data_list(self, target_data_list):

        if len(target_data_list) == 0:
            CustomMessageBox.warning(self.parent, "Data remove warning", "No file has been selected.")
            return

                
        message = "Are you sure you want to delete the selected data?<br>"
        for i, target_item in enumerate(target_data_list):
            if i == len(target_data_list)-1:
                message += "· " + target_item
            else:
                message += "· " + target_item + "<br>"
            
        # 선택된 파일들에 대해 사용자에게 확인 메시지 띄우기
        reply = CustomMessageBox.question(
            self.parent, 
            "File deletion", 
            message,
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        # 사용자가 '예'를 선택한 경우에만 삭제 진행
        if reply == QMessageBox.Yes:

            self.on_data_remove_requested(target_data_list)
        
    def update_list(self, file_name, file_data, unsaved_data_flag, hide_data_flag):
        # 이벤트 초기화
        self.on_item_clicked(None)
        self.on_item_double_clicked(None)

        # Target file 선택이 해제된 경우
        if file_name is None:
            self.selected_file_label.setText("")
            self.tree_view.clear_itmes()
            return
        
        # Target file 표시
        self.selected_file_label.setText(file_name)

        # Data의 헤더를 알파벳 순으로 정렬
        sorted_key_list, _ = get_sorted_indices(file_data.keys())
        sorted_header_list = []
        sorted_selected_flag = []
        sorted_icon_flag = []
        
        for i in range(len(sorted_key_list)):
            # 만약 hide_flag가 True일 경우, 항목으로 추가하지 않음
            if hide_data_flag[sorted_key_list[i]] is True:
                continue
            
            sorted_header_list.append(sorted_key_list[i].split("-")) # AA-marker-raw > ["AA", "makrer", "raw"] 식으로 변환
            sorted_selected_flag.append(False)
            sorted_icon_flag.append(unsaved_data_flag[sorted_key_list[i]])
            
        self.tree_view.add_items(sorted_header_list, sorted_selected_flag, sorted_icon_flag)
        
        # 수평 슬라이더를 가장 좌측으로 이동
        self.tree_view.horizontalScrollBar().setValue(0)