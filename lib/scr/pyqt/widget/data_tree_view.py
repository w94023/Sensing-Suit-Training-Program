from ....pyqt_base import *
from ....ui_common import *
from ....base import *

from .message_box import CustomMessageBox
from .tree_view import CustomDataTreeView
from .progress_dialog import ProgressDialog

class CustomDataTreeView(CustomDataTreeView):
    def __init__(self, data_handler, tree_view_header, click_event_actions, model=None, parent=None):
        self.parent = parent
        super().__init__(tree_view_header, model, parent)
        
        # 인스턴스 저장
        self.data_handler = data_handler
        
        # 선택된 data 이름 저장
        self.selected_items = None

        # 스레드 관리
        self.loading_thread = None

        # 오래 걸리는 작업을 처리하기 위한 dialog 생성
        self.loading_dialog = ProgressDialog("Data loading progress", self.parent)
        
        # 마우스 우클릭 이벤트를 위해 context menu policy 설정
        self.click_event_actions = click_event_actions
        if click_event_actions is not None and len(click_event_actions) != 0:
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.__show_context_menu)

        # 허용할 MIME 형식 리스트 정의
        allowed_formats = ['text/plain', 'text/uri-list']  # 텍스트와 URL 형식 허용

        # drop event callback 저장
        self.drop_event_callback = None

        # remove 이벤트 설정
        self.on_item_remove_requested = CustomEventHandler()

    def set_mime_data_format_filter(self, allowed_formats):
        self.allowed_formats = allowed_formats

    def set_drop_event_callback(self, drop_event_callback):
        self.drop_event_callback = drop_event_callback

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
        for action_name, callback in self.click_event_actions.items():
            contet_action = context_menu.addAction(action_name)
            contet_action.triggered.connect(callback)
        
        # 컨텍스트 메뉴 위치 표시
        context_menu.exec_(self.viewport().mapToGlobal(position))
   
    def _check_event_data_validity(self, event):
        # 이벤트 처리
        mime_data = event.mimeData()

        # 특정 MIME 형식만 허용하는 조건
        if any(fmt in mime_data.formats() for fmt in self.allowed_formats):
            return True
        else:
            return False

    def dragEnterEvent(self, event: QDragEnterEvent):
        """TreeView에 파일 drag 진입 시, 파일 명 및 url을 가지고 있다면 허용"""
        if self._check_event_data_validity(event):
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        """TreeView위에서 파일 drag 시, 파일 명 및 url을 가지고 있다면 허용"""
        if self._check_event_data_validity(event):
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        """TreeView에 파일 drop 시, 파일 명 및 url을 가지고 있다면 허용"""
        if self._check_event_data_validity(event):
            event.setDropAction(Qt.CopyAction)
            event.accept()

            # drop event callback이 등록되어 있다면 호출
            if self.drop_event_callback is not None:
                self.drop_event_callback()

        else:
            event.ignore()
            
    def remove_data(self):
        """TreeView 아이템 삭제하는 메서드"""

        if self.selected_items is None:
            return
        
        if len(self.selected_items) == 0:
            return

        target_item_keys = []        
        # 선택된 항목 수집
        for item in self.selected_items:
            
            # 선택된 항목에서 key 추출
            item_key = "-".join(item)
            target_item_keys.append(item_key)

        # 이벤트 호출
        self.on_item_remove_requested(target_item_keys)
