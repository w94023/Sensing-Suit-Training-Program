from ....pyqt_base import *
from ....ui_common import *

from .message_box import CustomMessageBox

class CustomDataTreeView(QTreeView):
    def __init__(self, tree_view_header, model=None, parent=None):
        """Data 표시를 위한 QTreeView

        Args:
            tree_view_header (_type_): _description_
            model (QModel, optional): TreeView에 연결할 모델. Defaults to None.
            parent (QWidget, optional): 부모 Widget 설정 (QMainWindow). Defaults to None.
        """
        
        self.parent = parent
        super().__init__(self.parent) 
        
        # flag
        self.__use_multi_selection_mode = True
        self.__use_double_click_event = True
        self.__use_no_data_image = True
        self.__use_icon_in_first_column = False
        
        # Icon 로드
        self.unsaved_data_icon = PyQtAddon.create_svg_icon("unsaved_json_data_icon.svg", 16, 16)
        
        # SVG background draw flag
        self.__draw_svg_background = False

        # header 설정 저장
        self.tree_view_header = tree_view_header
        
        # UI 초기화
        self.__init_ui()
        
        # QTreeView에 모델 설정
        if model is None:
            self.model = QStandardItemModel()
        else:
            self.model = model
            
        # 주어진 self.tree_view_header가 유효할 경우, TreeView의 헤더로 설정
        if self.tree_view_header is not None:
            if len(self.tree_view_header) > 0:
                self.model.setHorizontalHeaderLabels(self.tree_view_header)
        self.setModel(self.model)
        
        # 기본 선택 모드를 SingleSelection으로 설정
        self.setSelectionMode(QTreeView.SingleSelection)
        self.setSelectionBehavior(QTreeView.SelectRows)
        
        # 선택 항목 변경 시 시그널 연결
        self.selectionModel().selectionChanged.connect(self.__on_selection_changed)
        
        # 더블 클릭 시그널 연결
        self.doubleClicked.connect(self.__on_item_double_clicked)  
        
        # 범위 밖 클릭 및 더블클릭 시그널 연결
        self.viewport().installEventFilter(self)
        
        # TreeView 데이터
        self.__item_headers = []
        self.__item_selected_flags = []
        self.__item_icon_flags = []
        
        # 이벤트 설정
        self.on_item_double_clicked = CustomEventHandler()
        self.on_item_clicked = CustomEventHandler()
        
        self.update_list()
        
    def __init_ui(self):
        # SVG 렌더러 초기화 (SVG 이미지를 로드)
        self.svg_renderer = QSvgRenderer(PyQtAddon.convert_url(os.path.join(icons_directory, "no_data_icon.svg")))  # 여기에 SVG 파일 경로 입력
        
        # SVG 배경 그리기 여부를 제어하는 플래그
        self.draw_svg_background = True
        
        # 드래그 앤 드롭 설정
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        
        # 기타 설정
        self.setItemsExpandable(False)  # 항목 확장 불가
        self.setRootIsDecorated(False)  # 트리 루트 장식 없애기
        
        # 열 너비가 창 크기에 맞게 자동으로 확장되도록 설정
        self.header().setSectionResizeMode(QHeaderView.Stretch)
        
        # 스타일 설정
        self.setStyleSheet(f"""
                        QTreeView {{
                            background-color: {PyQtAddon.get_color("background_color")};
                            color: {PyQtAddon.get_color("title_text_color")};
                            font-family:{PyQtAddon.text_font};
                            border: none;
                            outline: none;
                        }}
                        QHeaderView::section {{
                            background-color: {PyQtAddon.get_color("point_color_1")};
                            color: {PyQtAddon.get_color("content_text_color")};
                            padding-left: 5px;
                            padding-right: 5px;
                            border: none;
                        }}
                        QTreeView::item:hover {{
                            background-color: {PyQtAddon.get_color("point_color_1")};
                            color: {PyQtAddon.get_color("content_text_color")};
                            border: none;
                        }}
                        QTreeView::item:selected {{
                            background-color: {PyQtAddon.get_color("point_color_5")};
                            color: {PyQtAddon.get_color("content_text_color")};
                            border: none;
                        }}
                        """
                        +PyQtAddon.vertical_scrollbar_style
                        +PyQtAddon.horizontal_scrollbar_style)
    
    def enable_multi_selection(self, enable):
        """
        Ctrl 혹은 Shift 누를 경우 multi selection 허용할 지 여부 (기본값:True)
        :param enable: True > multi selection 허용, False > multi selection 비허용
        """
        self.__use_multi_selection_mode = enable
        
    def enable_header(self, enable):
        """
        Header 표시할 지 여부를 설정하는 메서드 (기본값:True)
        :param enable: True > 헤더 표시, False > 헤더 숨김
        """
        self.setHeaderHidden(not enable)
        self.viewport().update()  # 트리뷰를 다시 그려서 설정 반영
        
    def enable_no_data_background(self, enable):
        """
        List item이 없을 때, no data 배경을 그릴지 여부를 설정하는 메서드 (기본값:True)
        :param enable: True > no data 배경 그리기, False > no data 배경 그리지 않기
        """
        self.__use_no_data_image = enable
        self.__draw_no_data_image()
        
    def enable_first_column_as_icon(self, enable):
        """첫 번째 열을 icon 출력에 사용할 지 여부를 설정하는 메서드 (기본값:False)

        Args:
            enable (bool): True > 아이콘 표시, False > 아이콘 미표시
        """
        self.__use_icon_in_first_column = enable
        
        # 아이콘 표시할 경우,
        if self.__use_icon_in_first_column:
            
            # 헤더의 항목 개수 반환
            column_count = self.model.columnCount()
            
            # 트리 뷰의 헤더 반환
            header = self.header()
            
            # 아이콘 열은 콘텐츠 크기에 맞춤
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            
            # 나머지 열은 창 크기에 맞춰 확장
            for i in range(1, column_count):
                header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 아이콘 표시 하지 않을 경우,   
        else:
            
            # 모든 열 창 크기에 맞춰 확장
            self.header().setSectionResizeMode(QHeaderView.Stretch)
        
        # TreeView item 업데이트
        self.update_list()
           
    def enable_double_click_event(self, enable):
        """
        Double click 이벤트 적용할 지 여부
        :param enable: True > 적용, False > 미적용
        """
        self.__use_double_click_event = enable
        
    def keyPressEvent(self, event):
        # use_multi_selection_mode = True가 아닐 시, single-selection으로 설정 후 종료
        if not self.__use_multi_selection_mode:
            self.setSelectionMode(QTreeView.SingleSelection)
            super().keyPressEvent(event)
            return
        
        # Ctrl 키나 Shift 키가 눌린 경우 MultiSelection 모드로 전환
        if event.key() == Qt.Key_Control or event.key() == Qt.Key_Shift:
            self.setSelectionMode(QTreeView.ExtendedSelection)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        # use_multi_selection_mode = True가 아닐 시, single-selection으로 설정 후 종료
        if not self.__use_multi_selection_mode:
            self.setSelectionMode(QTreeView.SingleSelection)
            super().keyPressEvent(event)
            return
        
        # Ctrl 키나 Shift 키가 해제된 경우 SingleSelection 모드로 복귀
        if event.key() == Qt.Key_Control or event.key() == Qt.Key_Shift:
            self.setSelectionMode(QTreeView.SingleSelection)
        super().keyReleaseEvent(event)
        
    def eventFilter(self, source, event):
        """클릭 이벤트 필터 메서드 > 빈 곳 클릭 및 더블 클릭 여부 확인"""
        if source == self.viewport():
            # 빈 곳을 클릭했을 때
            if event.type() == QEvent.MouseButtonPress:
                index = self.indexAt(event.pos())
                if not index.isValid():  # 빈 곳 클릭 확인
                    self.__clear_click_event()
            # 빈 곳을 더블 클릭했을 때
            elif event.type() == QEvent.MouseButtonDblClick:
                index = self.indexAt(event.pos())
                if not index.isValid():  # 빈 곳 더블 클릭 확인
                    self.__clear_double_click_event()
        return super().eventFilter(source, event)
    
    def __clear_click_event(self):
        """클릭으로 발생한 이벤트 및 강조 표시 초기화"""
        
        # 클릭으로 발생한 selection 해제
        self.clearSelection()
        
        # None 이벤트 호출
        self.on_item_clicked(None)

    def __clear_double_click_event(self):
        """더블 클릭으로 발생한 이벤트 및 강조 표시 초기화"""
    
        # 아이템 강조 표시 flag 초기화
        for i in range(len(self.__item_selected_flags)):
            self.__item_selected_flags[i] = False
            
        # 트리뷰 리스트 update
        self.update_list()
        
        # None 이벤트 호출
        self.on_item_double_clicked(None)
    
    def __on_item_double_clicked(self, index):
        """파일 리스트에서 항목을 더블 클릭했을 때 동작"""
        
        if not self.__use_double_click_event:
            return
        
        # 선택된 항목의 인덱스 행 가져오기
        row = index.row()
        
        # 열(헤더) 개수 확인
        column_count = self.model.columnCount()
        
        # icon을 첫 열에 표시 중일 경우, header의 첫 열은 의미 없으므로 삭제
        start_index = 1 if self.__use_icon_in_first_column else 0
        
        # 아이템 헤더 반환
        headers = []
        for i in range(start_index, column_count):
            headers.append(self.model.item(row, i).text())
        self.on_item_double_clicked(headers)

        # 아이템 강조 표시 flag 초기화
        for i in range(len(self.__item_selected_flags)):
            self.__item_selected_flags[i] = False
        
        # 선택된 아이템 강조 표시
        if row < len(self.__item_selected_flags):
            self.__item_selected_flags[row] = True
            self.update_list()
        
    def __get_selected_items(self):
        # 선택된 항목의 인덱스 가져오기
        selected_indexes = self.selectionModel().selectedIndexes()
        
        # 행을 기준으로 선택된 인덱스를 정리
        selected_rows = set(index.row() for index in selected_indexes)
        
        # icon을 첫 열에 표시 중일 경우, header의 첫 열은 의미 없으므로 삭제
        start_index = 1 if self.__use_icon_in_first_column else 0

        # 각 선택된 행의 모든 열 데이터를 가져옴
        selected_items = []
        for row in selected_rows:
            items = []
            for column in range(start_index, self.model.columnCount()):  # 모든 열에 대해 데이터를 가져옴
                index = self.model.index(row, column)
                items.append(index.data())
                
            # 선택된 항목의 데이터를 리스트로 저장
            selected_items.append(items)
            
        return selected_items
    
    def __on_selection_changed(self, selected, deselected):
        # 선택 항목 변경 시 현재 선택된 항목을 가져와 출력
        selected_items = self.__get_selected_items()
        self.on_item_clicked(selected_items)
        
    def __draw_no_data_image(self):
        if len(self.__item_headers) == 0 and self.__use_no_data_image:
            self.__draw_svg_background = True
        else:
            self.__draw_svg_background = False
            
        self.viewport().update()  # 트리뷰를 다시 그려서 설정 반영
                      
    def paintEvent(self, event):
        def render_svg_with_aspect_ratio(painter, ratio):
            """SVG를 트리뷰 영역에 비율을 유지하면서 그리는 메서드"""
            # 트리뷰의 그릴 수 있는 전체 영역
            available_rect = self.viewport().rect()

            # SVG 원본 크기
            svg_size = self.svg_renderer.defaultSize()

            # 가로 세로 비율을 유지하면서 영역에 맞게 크기 조정
            aspect_ratio = min(available_rect.width() / svg_size.width(), available_rect.height() / svg_size.height())

            # 새 크기 계산 (비율 유지)
            new_width = svg_size.width() * aspect_ratio * ratio
            new_height = svg_size.height() * aspect_ratio * ratio

            # 중앙에 배치하기 위한 좌표 계산
            x = (available_rect.width() - new_width) / 2
            y = (available_rect.height() - new_height) / 2

            # 비율을 유지한 SVG 이미지를 그리기
            target_rect = QRectF(x, y, new_width, new_height)
            self.svg_renderer.render(painter, target_rect)

        # 부모의 기본 그리기 동작 호출 (헤더 포함)
        super().paintEvent(event)

        # draw_svg_background가 True일 때만 SVG 이미지를 그리기
        if self.__draw_svg_background:
            painter = QPainter(self.viewport())  # 트리뷰 본체 영역에 그리기
            render_svg_with_aspect_ratio(painter, 0.25)  # 비율 유지하면서 SVG 그리기

    def add_items(self, headers, selected_flags, icon_flags):
        """List의 item 추가하는 메서드

        Args:
            headers (list of str | list of str list): 추가하려는 item의 text
            selected_flags (list of bool): 추가된 item의 background color 강조 여부
            icon_flags (list of bool): 추가된 item의 icon 출력 여부 (첫 열이 icon으로 사용 중일 때만 정상 출력)
        """
        
        self.__item_headers = headers
        self.__item_selected_flags = selected_flags
        self.__item_icon_flags = icon_flags
        
        self.update_list()

    def add_items_without_selected_flags(self, headers, icon_flags):
        item_selected_flags = []
        for i in range(len(headers)):
            if headers[i] in self.__item_headers:
                target_index = self.__item_headers.index(headers[i])
                item_selected_flags.append(self.__item_selected_flags[target_index])
            else:
                item_selected_flags.append(False)

        self.__item_headers = headers
        self.__item_selected_flags = item_selected_flags
        self.__item_icon_flags = icon_flags

        self.update_list()
        
    def add_item(self, text, selected_flag, icon_flag):
        self.__item_headers.append(text)
        self.__item_selected_flags.append(selected_flag)
        self.__item_icon_flags.append(icon_flag)
            
        self.update_list()
        
    def __create_item(self, text, use_point_color, use_icon):
        """QStandardItem 생성 메서드

        Args:
            text (str): Item text
            use_point_color (bool): Item point 배경색 사용 우무
            use_icon (bool): Item icon 배치 유무

        Returns:
            QStandardItem: Item 반환
        """
        
        item = QStandardItem(text)
        
        # 수정 불가능
        item.setEditable(False)
        
        # 배경색 및 글자색 설정
        if use_point_color:
            item.setBackground(PyQtAddon.get_color("point_color_6", option=2)) # 배경색 설정
            item.setForeground(PyQtAddon.get_color("content_text_color", option=2)) # 글자색 설정
        else:
            item.setBackground(PyQtAddon.get_color("background_color", option=2)) # 배경색 설정
            item.setForeground(PyQtAddon.get_color("content_text_color", option=2)) # 글자색 설정
            
        # 아이콘 설정
        if use_icon:
            item.setIcon(self.unsaved_data_icon)
            
        return item
              
    def __add_tree_item(self, header, use_point_color, use_icon):
        """아이템을 QTableWidget에 추가하는 메서드"""
        item_row = []
        
        # self.__use_icon_in_first_column == True일 경우, 첫 열에 아이콘 추가
        if self.__use_icon_in_first_column is True:
            item_row.append(self.__create_item("", use_point_color, use_icon))
            
        # header가 단일 string으로 주어진 경우 분해하지 않고 header 하나를 item text로 설정
        if isinstance(header, str):
            item_row.append(self.__create_item(header, use_point_color, False))
            
        # header가 list일 경우, 분해하여 각 요소를 각 열의 item text로 설정
        elif isinstance(header, list):
            for text in header:
                item_row.append(self.__create_item(text, use_point_color, False))
            
        self.model.appendRow(item_row)      
                
    def update_list(self):
        """List의 item update하는 메서드"""
        # 항목만 삭제 (헤더는 유지)
        self.model.removeRows(0, self.model.rowCount())

        row_count = 0
        # 목록에 추가
        for i in range(len(self.__item_headers)):
            self.__add_tree_item(self.__item_headers[i], self.__item_selected_flags[i], self.__item_icon_flags[i])
            row_count += 1
        
        # 추가된 항목에 따라 no data svg image 표시
        self.__draw_no_data_image()
    
    def clear_itmes(self):
        """TreeView 내의 모든 항목 삭제하는 메서드"""
        
        self.__item_headers.clear()
        self.__item_selected_flags.clear()
        self.__item_icon_flags.clear()

        # 이벤트 초기화
        self.on_item_clicked(None)
        self.on_item_double_clicked(None)
        
        # 리스트 업데이트
        self.update_list()
        
    def remove_item(self):
        """선택된 파일을 리스트 에서 삭제하는 메서드"""
        # 선택된 항목의 인덱스 가져오기
        selected_indexes = self.selectionModel().selectedIndexes()

        if not selected_indexes:
            CustomMessageBox.warning(self.parent, "Warning", "Please select the data you want to delete.")
            return
        else:
            # 선택된 항목들의 인덱스 가져옴
            for selected_index in selected_indexes:
                # 해당 항목을 모델에서 제거
                self.model.removeRow(selected_index.row(), selected_index.parent())

            self.update_list()

    def set_item_focus(self, file_name):
        # 주어진 파일 이름이 __item_header에 있는 지 확인
        if file_name in self.__item_headers:
            target_index = self.__item_headers.index(file_name)

            # 포커스 활성화
            self.__item_selected_flags[target_index] = True
        
            self.update_list()


    def release_double_clicked_target(self):
        # 더블 클릭된 항목의 focus를 해제하고, 이벤트 호출하는 메서드
        if not self.__use_double_click_event:
            return
        
        # 아이템 강조 표시 flag 초기화
        for i in range(len(self.__item_selected_flags)):
            self.__item_selected_flags[i] = False

        # 이벤트 호출
        self.on_item_double_clicked(None)

        # 리스트 업데이트
        self.update_list()