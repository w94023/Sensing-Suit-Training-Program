from .common import *
from .tree_view import *
                
class CustomDataTreeView(CustomDataTreeView):
    def __init__(self, json_data_manager, csv_data_tree_view_header, model=None, parent=None):
        """CustomDataTreeView에서 drop event, 마우스 우클릭 event 추가한 위젯

        Args:
            data_loader: CSV로부터 pd.DataFrame 불러오기 위한 인스턴스
            json_data_list_viewer: target file 지정을 위한 data list viewer 인스턴스
            csv_data_tree_view_header: 자식 클래스 매개 변수
        """
        self.parent = parent
        super().__init__(csv_data_tree_view_header, model, parent)
        
        # 인스턴스 저장
        self.json_data_manager = json_data_manager
        
        # 선택된 data 이름 저장
        self.selected_items = None
        
        # 마우스 우클릭 이벤트를 위해 context menu policy 설정
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__show_context_menu)
        
    def __on_selection_changed(self, selected, deselected):
        """self.selected_items 사용을 위해 부모 클래스 __on_selection_changed 재정의"""
        
        # 선택 항목 변경 시 현재 선택된 항목을 가져와 출력
        self.selected_items = self.__get_selected_items()
        self.on_item_clicked(self.selected_items)

    def _get_row_data(self, row):
        """선택된 행(row)의 모든 열 데이터를 리스트로 반환"""
        
        # icon을 첫 열에 표시 중일 경우, header의 첫 열은 의미 없으므로 삭제
        start_index = 1 if self.__use_icon_in_first_column else 0
        
        row_data = []
        # 모델에서 해당 행의 각 열 데이터를 가져옴
        for column in range(start_index, self.model.columnCount()):
            index = self.model.index(row, column)
            row_data.append(index.data())  # 열의 데이터를 가져옴
        return row_data
        
    def mousePressEvent(self, event: QMouseEvent):
        """TreeView에서 마우스 우클릭 시, 우클릭 된 항목이 이미 선택된 항목 중 하나일 경우,
        항목 선택이 해제되지 않도록 선별하는 메서드"""
        # 우클릭일 경우
        if event.button() == Qt.RightButton:
            # TreeView에서 선택된 항목이 없을 경우
            if self.selected_items is None or len(self.selected_items) == 0:
                # 우클릭으로 아이템 선택 허용
                super().mousePressEvent(event)
            
            # TreeView에서 이미 선택된 항목이 있을 경우
            else:
                # 클릭된 위치에서 인덱스를 가져옴
                index = self.indexAt(event.pos())
                
                # 아이템이 클릭되었을 경우
                if index.isValid():
                    # 클릭된 항목의 행(row)에 대한 모든 데이터를 가져오기
                    row = index.row()
                    selected_item = self._get_row_data(row)
                    
                    # 클릭된 아이템이 좌클릭으로 선택된 아이템에 포함되어 있을 경우
                    if selected_item in self.selected_items:
                        # 기존의 mousePressEvent 동작을 무시하고, 선택 해제를 방지
                        event.accept()
                        
                    # 클릭된 아이템이 좌클릭으로 선택된 아이템에 포함되어 있찌 않을 경우  
                    else:
                        # 우클릭으로 아이템 선택 허용
                        super().mousePressEvent(event)
                        
                # 빈 공간이 클릭 되었을 경우
                else:
                    # 기존의 mousePressEvent 동작을 무시하고, 선택 해제를 방지
                    event.accept()

        else:
            # 우클릭이 아닌 다른 클릭은 기본 동작을 처리
            super().mousePressEvent(event)
        
    def __show_context_menu(self, position):
        """TreeView에서 항목에 마우스 우클릭 시 보여주는 메뉴 설정하는 메서드"""
        
        # 컨텍스트 메뉴 생성
        context_menu = QMenu(self)

        # CSV 저장 액션 추가
        export_action = context_menu.addAction("Export CSV file")
        export_action.triggered.connect(self.__export_to_csv)
        
        # 컨텍스트 메뉴 위치 표시
        context_menu.exec_(self.viewport().mapToGlobal(position))

    def __export_to_csv(self):
        """TreeView에서 선택된 항목 CSV 파일로 export하는 메서드"""
        
        # CSV 파일 저장 경로 선택
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "", QFileDialog.ShowDirsOnly)
        
        # JSON data manager로부터 현재 타겟의 데이터 불러오기
        data, _, _ = self.json_data_manager.get_json_data()
        
        # 선택된 item에 대해 csv 파일 export 시작
        for item in self.selected_items:
            
            # item이 불러온 data의 key에 존재하는 지 확인
            item_key = "-".join(item)
            if item_key in data.keys():
                
                # data value 저장
                save_csv_file(os.path.join(directory_path, item_key+".csv"), data[item_key])

    
    def __cut_string_after_substring(self, main_string, sub_string):
        """main string에서 sub string 잘라내고 반환하는 메서드

        Args:
            main_string (str): 대상 string
            sub_string (str): 자를 string

        Returns:
            cut_string (str): 주어진 sub_string 이전 까지의 main_string 반환
        """
        
        # 특정 문자열이 main_string에 있는지 확인
        index = main_string.find(sub_string)
        
        if index != -1:
            # 특정 문자열 이전까지의 부분을 잘라내기
            # index + len(substring) 하면 substring까지 포함해서 잘라냄
            return main_string[:index]
        else:
            # 특정 문자열이 없는 경우 원래 문자열 반환
            return main_string
        
    def __check_validity_of_file_name(self, file_name):
        """파일 이름이 유효한 지 확인하는 메서드 (data name_data type_data state.csv)

        Args:
            file_name (str): 검사 대상 파일명

        Returns:
            validity, data name, data type, data state (bool, str, str, str): Format 유효성 여부(.csv파일 인 지) validity로 반환. 인식 불가능한 data name, data type, data state는 None타입으로 반환 
        """
        
        # .csv 포함되어 있는 지 확인
        if ".csv" in file_name:
            cut_string = self.__cut_string_after_substring(file_name, ".csv")
            
            # 주어진 file이 marker file 인 지 확인
            if "_Marker" in cut_string:
                motion_name = self.__cut_string_after_substring(cut_string, "_Marker")
                return True, motion_name, "marker", "raw"
            
            # 주어진 file이 sensor file 인 지 확인
            elif "_Sensor" in cut_string:
                motion_name = self.__cut_string_after_substring(cut_string, "_Sensor")
                return True, motion_name, "sensor", "raw"
            
            else:
                return True, None, None, None
        else:
            CustomMessageBox.critical(None, "Data import error", "The data is in an incorrect format.")
            return False, None, None, None
            
    def dragEnterEvent(self, event: QDragEnterEvent):
        """TreeView에 파일 drag 진입 시, 파일 명 및 url을 가지고 있다면 허용"""
        if event.mimeData().hasText() and event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        """TreeView위에서 파일 drag 시, 파일 명 및 url을 가지고 있다면 허용"""
        if event.mimeData().hasText() and event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """TreeView에 파일 drop 시, 파일 명 및 url을 가지고 있다면 허용"""
        if event.mimeData().hasText() and event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            
            # 드랍된 파일의 파일 명 불러오기
            file_name = event.mimeData().text()
            
            # 파일 명의 유효성 검사 및 name, type, state 분리
            validity, data_name, data_type, data_state = self.__check_validity_of_file_name(file_name)
            
            # 유효하지 않을 경우 작업 종료
            if not validity:
                CustomMessageBox.critical(None, "Data import error", "The file format is incorrect.")
                return
            
            # data_name, data_type, data_state의 정확한 입력을 위해 유저에게 dialog로 받아옴
            # self.__check_validity_of_file_name 메서드로 인식된 name, type, state를 default값으로 사용
            dialog = CustomComboBoxDialog([data_name, data_type, data_state])
                    
            # 사용자가 OK를 클릭한 경우 선택된 항목을 가져옴
            if dialog.exec_() == QDialog.Accepted:
                
                # 드랍된 파일의 data_type 저장
                data_type = dialog.get_selections()[1]
                
                # 드랍된 파일의 path 불러오기 (url)
                file_path = event.mimeData().urls()[0].toLocalFile()
                
                # 드랍된 csv파일로 부터 pd.DataFrame 불러오기
                key = dialog.get_selections()[0]+"-"+dialog.get_selections()[1]+"-"+dialog.get_selections()[2]
                df = load_csv_file(file_path, data_type, parent=self.parent)

                # 파일 읽어오기에 실패했을 경우, 이벤트 종료
                if df is None:
                    return
                
                # 로드된 json 파일에 csv파일로부터 import한 데이터 추가
                self.json_data_manager.add_data_to_target_json_file(key, df)
                
            # 사용자가 Cancel을 클릭한 경우 작업 종료
            else:
                CustomMessageBox.critical(None, "Data import error", "The task has been canceled.")
                return
                
        else:
            event.ignore()
            
    def remove_data(self):
        """TreeView 아이템 삭제하는 메서드"""
        
        # 선택된 항목 JSON data manager에 삭제 요청
        for item in self.selected_items:
            
            # 선택된 항목에서 key 추출
            item_key = "-".join(item)
            
            # JSON data manager에 삭제 요청
            self.json_data_manager.remove_data_to_target_json_file(item_key)
            
class JSONDataViewer(QWidget):                 
    def __init__(self, json_data_manager, json_list_viewer, parent=None):
        """JSON 파일 내의 데이터 목록을 보여주는 위젯

        Args:
            json_list_viewer: JSON data list viewer 연결
            parent: 부모 객체. Defaults to None.
        """
        
        self.parent = parent
        super().__init__(self.parent)
        
        # JSON data manager 저장 및 이벤트 연결
        self.json_data_manager = json_data_manager
        self.json_data_manager.on_target_file_changed += self.__update_list
        
        # UI 초기화
        self.__init_ui()
        
        # 이벤트 생성
        self.on_item_clicked = CustomEventHandler()
        self.on_item_double_clicked = CustomEventHandler()

        # 이벤트 연결
        self.csv_data_tree_view.on_item_clicked += self.on_item_clicked
        self.csv_data_tree_view.on_item_double_clicked += self.on_item_double_clicked

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


        # CSV data tree view 생성
        self.csv_data_tree_view = CustomDataTreeView(self.json_data_manager, ["", "Name", "Type", "State"], None, self.parent)
        self.csv_data_tree_view.enable_first_column_as_icon(True)

        # Optitrack .tak 파일 raw data tree view 생성
        self.tak_raw_data_tree_view = CustomDataTreeView(self.json_data_manager, ["", "Name", "Type", "State"], None, self.parent)
        self.tak_raw_data_tree_view.enable_first_column_as_icon(True)

        # Optitrack .tak 파일 interpolated data tree view 생성
        self.tak_interpolated_data_tree_view = CustomDataTreeView(self.json_data_manager, ["", "Name", "Type", "State"], None, self.parent)
        self.tak_interpolated_data_tree_view.enable_first_column_as_icon(True)

        # Optitrack .tak 파일 smoothed data tree view 생성
        self.tak_smoothed_data_tree_view = CustomDataTreeView(self.json_data_manager, ["", "Name", "Type", "State"], None, self.parent)
        self.tak_smoothed_data_tree_view.enable_first_column_as_icon(True)

        # QTabWidget 생성
        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(self.csv_data_tree_view, "CSV file")
        self.tab_widget.addTab(self.tak_raw_data_tree_view, "Tak raw file")
        self.tab_widget.addTab(self.tak_interpolated_data_tree_view, "Tak interpolated file")
        self.tab_widget.addTab(self.tak_smoothed_data_tree_view, "Tak smoothed file")
        content_layout.addWidget(self.tab_widget)

        # - 버튼 생성 (파일 삭제)
        self.remove_button = QPushButton()
        self.remove_button.clicked.connect(self.csv_data_tree_view.remove_data)
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
            
    def __update_list(self, file_name, file_data, unsaved_data_flag, hide_data_flag):
        """JSON data manager의 data가 update된 경우, 위젯 내 TreeView 업데이트"""

        # Target file 선택이 해제되었거나, 오류가 발생한 경우
        if file_name is None:
            self.selected_file_label.setText("")
            self.csv_data_tree_view.clear_itmes()
            return
        
        # 이벤트 초기화
        self.on_item_clicked(None)
        self.on_item_double_clicked(None)

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
            
        self.csv_data_tree_view.add_items(sorted_header_list, sorted_selected_flag, sorted_icon_flag)
    