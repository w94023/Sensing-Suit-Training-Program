from ..common import *
from .common import *

from ...pyqt.widget import (FileDataViewer, CustomDataTreeView, CustomComboBox, CustomInputDialog, CustomMessageBox)

class CustomComboBoxDialog(QDialog):
    def __init__(self, default_options=None, parent=None):
        """Data name, type, state 선택할 수 있는 combo box 세 개를 가진 QDialog

        Args:
            default_options (str list): 각 콤보 박스의 기본값. Defaults to None.
        """
        
        # 각 콤보 박스 옵션 설정
        data_name_list = ["AA", "FE", "ML", "CB1", "CB2", "CB3", "VALID", "TEST", "..."]
        data_type_list = ["marker", "sensor", "wireframe"]
        data_state_list = ["raw", "refined"]
        
        # default_index 유효성 검사
        if default_options is None:
            default_index = [0, 0, 0]
        else:
            if len(default_options) != 3:
                default_index = [0, 0, 0]
                
            else:
                default_index = [
                    data_name_list. index(default_options[0]) if default_options[0] in data_name_list  else 0,
                    data_type_list. index(default_options[1]) if default_options[1] in data_type_list  else 0,
                    data_state_list.index(default_options[2]) if default_options[2] in data_state_list else 0
                ]
            
        self.parent = parent
        super().__init__(self.parent)
        self.setWindowTitle("Select Options")

        # 레이아웃 설정
        layout = QVBoxLayout(self)

        # Data name dropdown
        self.data_name_combo = CustomComboBox(self)
        self.data_name_combo.addItems(data_name_list)
        layout.addWidget(QLabel("Select data name:"))
        layout.addWidget(self.data_name_combo)
        layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.data_name_combo.setCurrentIndex(default_index[0])
        
        # data name dropbox의 option이 ...일 경우, 이벤트 발생시킬 수 있도록 콜백 연결
        self.data_name_combo.activated[str].connect(self.__on_data_name_changed)

        # Data type dropdown
        self.data_type_combo = CustomComboBox(self)
        self.data_type_combo.addItems(data_type_list)
        layout.addWidget(QLabel("Select data type:"))
        layout.addWidget(self.data_type_combo)
        layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.data_type_combo.setCurrentIndex(default_index[1])

        # Data state dropdown
        self.data_state_combo = CustomComboBox(self)
        self.data_state_combo.addItems(data_state_list)
        layout.addWidget(QLabel("Select data state:"))
        layout.addWidget(self.data_state_combo)
        layout.addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.data_state_combo.setCurrentIndex(default_index[2])

        # OK, Cancel 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {PyQtAddon.get_color("background_color")};
                border: none;
            }}
            QLabel {{
                color: {PyQtAddon.get_color("title_text_color")};
                font-family: {PyQtAddon.text_font};
                border: none;
            }}
            QPushButton {{
                background-color: {PyQtAddon.get_color("point_color_1")};
                color: {PyQtAddon.get_color("title_text_color")};
                padding: 4px 8px;
                border-radius: 0px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {PyQtAddon.get_color("point_color_2")};
                border: none;
            }}
        """)
        
    def __get_custom_file_name(self):
        result = CustomInputDialog.getText(self.parent, "Data import", "Please enter the file name.", "")
        file_name = result[0]
        reply = result[1]

        # 유저가 cancel을 선택했을 경우
        if not reply:
            return None

        # 파일명에 사용할 수 없는 특수문자 정의
        invalid_chars = r'[\\/:*?"<>|]'
        
        if not file_name:
            CustomMessageBox.warning(self.parent, "Data import", "File name cannot be empty.")
            self.__get_custom_file_name()
        elif re.search(invalid_chars, file_name):
            CustomMessageBox.warning(self.parent, "Data import", "File name contains invalid characters: \\/:*?\"<>|")
            self.__get_custom_file_name()
        else:
            return file_name

    def __on_data_name_changed(self, text):
        # 유저가 입력한 데이터가 ...일 경우, 직접 file name 수정할 수 있도록 Dialog 생성
        if text == "...":
            file_name = self.__get_custom_file_name()

            if file_name is None:
                return
        
            # ... 삭제 후, 유저가 입력한 file name으로 변경
            target_index = self.data_name_combo.findText("...")
            self.data_name_combo.setItemText(target_index, file_name)
            
            # ... 항목 추가
            self.data_name_combo.addItem("...")
        
    def get_selections(self):
        """선택된 항목을 반환

        Returns:
            str list: [data name, data type, data state]
        """
        # 선택된 항목을 반환
        return [self.data_name_combo.currentText(), self.data_type_combo.currentText(), self.data_state_combo.currentText()]

class DataImportThread(BackgroundThreadWorker):
    data_import_finished = pyqtSignal(bool, str, pd.DataFrame, Exception)
    
    def __init__(self, file_path, data_type, key, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.file_path = file_path
        self.data_type = data_type
        self.key = key

    def run(self):
        self.update_progress(10)

        df = load_csv_file(self.file_path, self.data_type, parent=self.parent)

        self.update_progress(100)

        # 파일 읽어오기에 실패했을 경우, 이벤트 종료
        if df is None:
            self.data_import_finished.emit(False, None, pd.DataFrame(), Exception("Failed to load data fro .csv file"))
        
        else:
            self.data_import_finished.emit(True, self.key, df, Exception())

class CustomDataTreeView(CustomDataTreeView):
    def __init__(self, data_handler, tree_view_header, model=None, parent=None):
        """CustomDataTreeView에서 drop event, 마우스 우클릭 event 추가한 위젯

        Args:
            data_loader: CSV로부터 pd.DataFrame 불러오기 위한 인스턴스
            json_data_list_viewer: target file 지정을 위한 data list viewer 인스턴스
            tree_view_header: 자식 클래스 매개 변수
        """
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
        data = self.data_handler.file_data

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
            
    def __get_data_info_from_user(self, data_name, data_type, data_state):
        # treeview로 드랍된 파일의 data name, data type, data state를 유저에게 받아오고, 유효성 검사하는 메서드
        
        # data_name, data_type, data_state의 정확한 입력을 위해 유저에게 dialog로 받아옴
        dialog = CustomComboBoxDialog([data_name, data_type, data_state])
        
        if dialog.exec_() == QDialog.Accepted:
            # 사용자가 OK를 클릭한 경우 선택된 항목을 가져옴
            selections = dialog.get_selections()
            
            # 선택된 항목 분류
            new_data_name = selections[0]
            new_data_type = selections[1]
            new_data_state = selections[2]
            
            if "-" in new_data_name:
                CustomMessageBox.critical(None, "Data import error", "'-' cannot be used in a name for the data.")
                return self.__get_data_info_from_user(data_name, data_type, data_state)
            
            if new_data_type != "marker" and new_data_type != "sensor" and new_data_type != "wireframe":
                CustomMessageBox.critical(None, "Data import error", "Invalid data type")
                return None, None, None
            
            if new_data_state != "raw" and new_data_state != "refined":
                CustomMessageBox.critical(None, "Data import error", "Invalid data state")
                return None, None, None
            
            return new_data_name, new_data_type, new_data_state
                
        else:
            # 사용자가 Cancel을 클릭한 경우 작업 종료
            CustomMessageBox.warning(None, "Data import error", "The task has been canceled.")
            return None, None, None

    def dropEvent(self, event: QDropEvent):
        """TreeView에 파일 drop 시, 파일 명 및 url을 가지고 있다면 허용"""
        if event.mimeData().hasText() and event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            if self.loading_thread is not None:
                CustomMessageBox.ciritical(self.parent, "Data import error", "The previous data load task has not been completed.")
                return
            
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
            data_name, data_type, data_state = self.__get_data_info_from_user(data_name, data_type, data_state)
            
            if data_name is None:
                return
            
            # 드랍된 파일의 path 불러오기 (url)
            file_path = event.mimeData().urls()[0].toLocalFile()
            
            # 드랍된 csv파일로 부터 pd.DataFrame 불러오기
            key = data_name+"-"+data_type+"-"+data_state
            
            # 키 유효성 검사
            if len(key.split('-')) != 3:
                CustomMessageBox.critical(None, "Data import error", "The data key is incorrect.")
                return
            
            # 작업 시작 window 표시
            self.loading_dialog.start_progress()
            
            # 백그라운드 스레드에서 data load 작업 수행
            self.loading_thread = DataImportThread(file_path, data_type, key, self.parent)
            self.loading_thread.data_import_finished.connect(self.__on_data_import_finished)
            self.loading_dialog.set_worker(self.loading_thread) # 백그라운드 스레드 설정
            self.loading_thread.start()
                
        else:
            event.ignore()
    
    def __on_data_import_finished(self, is_succeed, key, df):
        if is_succeed:
            # 로드된 json 파일에 csv파일로부터 import한 데이터 추가
            self.data_handler.add_data_to_target_file(key, df)

        self.loading_dialog.stop_progress()
        self.loading_thread = None
        self.loading_dialog.set_worker(self.loading_thread)
            
    def remove_data(self):
        """TreeView 아이템 삭제하는 메서드"""

        if self.selected_items is None:
            return
        
        if len(self.selected_items) == 0:
            return

        target_item_keys = []        
        # 선택된 항목 JSON data manager에 삭제 요청
        for item in self.selected_items:
            
            # 선택된 항목에서 key 추출
            item_key = "-".join(item)
            target_item_keys.append(item_key)
            
        # JSON data manager에 삭제 요청
        self.data_handler.remove_data_from_target_file(target_item_keys)
        
class PreparationDataViewer(FileDataViewer):
    def __init__(self, data_handler, parent=None):
        tree_view = CustomDataTreeView(data_handler, ["", "Name", "Type", "State"])
        tree_view.enable_first_column_as_icon(True)
        super().__init__(tree_view, parent)

        # 이벤트 연결
        self.on_data_remove_requested += self.__remove_data
        
        # data handler 저장 및 이벤트 연결
        self.data_handler = data_handler
        self.data_handler.on_target_data_changed += self.__on_target_data_changed
        
    def __on_target_data_changed(self, file_name, data, unsaved_flag, hide_flag):
        self.update_list(file_name, data, unsaved_flag, hide_flag)

    def __remove_data(self, target_data_list):
        self.data_handler.remove_data_from_target_file(target_data_list)