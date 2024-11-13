from .common import *
from .tree_view import *

target_filename_extension = '.h5'


class CustomModel(QStandardItemModel):
    def __init__(self):
        super().__init__()

    def set_data_viewer(self, data_viewer):
        self.data_viewer = data_viewer

    def mimeData(self, indexes):
        mime_data = QMimeData()
        if indexes:
            if self.data_viewer is None:
                CustomMessageBox.critical(None, "Error", "Data HTML conversion error - Data viewer is not connected.")
                return mime_data
            
            if self.data_viewer.tree_view.target_file_name is None:
                CustomMessageBox.critical(None, "Error", "Please double-click to load the data before sending it.")
                return mime_data
            
            item_name = self.itemFromIndex(indexes[0]).text()
            if item_name != self.data_viewer.tree_view.target_file_name:
                CustomMessageBox.critical(None, "Error", "The loaded data is different from the data you are trying to send.")
                return mime_data
            
            # MIME 데이터에 HTML 테이블 삽입
            mime_data.setHtml("")

            # 딕셔너리 데이터를 JSON 문자열로 직렬화하여 QMimeData에 추가
            json_data = json.dumps(self.data_viewer.tree_view.target_file_data)
            mime_data.setData("application/json", json_data.encode('utf-8'))

        return mime_data

class JSONListViewer(QWidget):
    def __init__(self, json_data_manager, parent=None):
        self.parent = parent
        super().__init__(self.parent)
        
        self.json_data_manager = json_data_manager
        self.json_data_manager.on_target_file_changed += self.__on_target_file_changed

        # 디렉토리 설정
        self.directory = json_directory

        # QFileSystemWatcher 설정 (파일 시스템 변화 감시)
        self.watcher = QFileSystemWatcher([self.directory])
        self.watcher.directoryChanged.connect(self.__update_list)
        
        # List window에서 표시 중인 json 파일 목록
        self.json_file_display_list = []
        self.json_file_unsaved_flags = []
        
        # 현재 선택된 JSON 파일
        self.selected_items = None
        
        # UI 초기화
        self.init_ui()

        # 파일 리스트 초기화
        self.__update_list()

    def init_ui(self):
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
        
        # TreeView 모델 생성
        self.model = CustomModel()

        # JSON file showing tree view 생성
        self.tree_view = CustomDataTreeView(["", "File name"], model=None, parent=self.parent)
        self.tree_view.enable_first_column_as_icon(True)
        # tree view 이벤트 등록
        self.tree_view.on_item_clicked += self.__on_item_clicked
        self.tree_view.on_item_double_clicked += self.__on_file_double_click
        
        # Save 버튼 생성
        self.save_button = create_tree_view_button("save_json_data_button_icon.svg", 20, 20, self.save_files)
        
        # Refresh 버튼 생성
        self.refresh_button = create_tree_view_button("refresh_json_data_button_icon.svg", 20, 20, self.refresh_list)

        # Rename 버튼 생성
        self.rename_button = create_tree_view_button("rename_json_data_button_icon.svg", 20, 20, self.rename_file)
        
        # + 버튼 생성 (파일 추가)
        self.add_button = create_tree_view_button("plus_button_icon.svg", 20, 20, self.add_file)

        # - 버튼 생성 (파일 삭제)
        self.remove_button = create_tree_view_button("minus_button_icon.svg", 20, 20, self.remove_file)
        
        # 버튼을 오른쪽으로 정렬시키기 위한 spacer 추가
        spacer = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # 버튼 레이아웃 설정
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.rename_button)
        button_layout.addWidget(self.save_button)
        button_layout.addItem(spacer)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        
        # 위젯 추가
        content_layout.addWidget(self.tree_view)
        content_layout.addLayout(button_layout)

    def __on_target_file_changed(self, file_name, file_data, unsaved_data_flag, hide_data_flag):
        # 리스트 초기화
        self.model.clear()  

        json_file_unsaved_flags = []
        for json_file_name in self.json_file_display_list:
            if json_file_name in self.json_data_manager.data_hist.keys():
                is_unsaved_data_existed = False
                for unsaved_flag in self.json_data_manager.data_hist[json_file_name][1].values():
                    if unsaved_flag is True:
                        is_unsaved_data_existed = True
                        break

                for hide_flag in self.json_data_manager.data_hist[json_file_name][2].values():
                    if hide_flag is True:
                        is_unsaved_data_existed = True
                        break
                
                if is_unsaved_data_existed is True:
                    json_file_unsaved_flags.append(True)
                else:
                    json_file_unsaved_flags.append(False)
            
            else:
                json_file_unsaved_flags.append(False)

        self.tree_view.add_items_without_selected_flags(self.json_file_display_list, json_file_unsaved_flags)
        
    def __update_list(self):
        """디렉토리의 .json 파일만 불러와 리스트에 추가"""
        # 리스트 초기화
        self.model.clear()  
        
        # 파일 목록 초기화
        file_names = []

        # Directory에 존재하는 파일 읽어오기
        for file_name in os.listdir(self.directory):

            # 파일인지 확인하고, 확장자가 target_filename_extension 인지 확인
            if os.path.isfile(os.path.join(self.directory, file_name)) and file_name.endswith(target_filename_extension):
                
                # JSON 파일일 경우, 목록에 추가
                file_names.append(file_name)
                
        self.json_file_unsaved_flags = [False] * len(file_names)

        # TreeView에 item 추가
        self.tree_view.add_items_without_selected_flags(file_names, self.json_file_unsaved_flags)

        # 인스턴스 데이터로 저장
        # (add file 메서드 호출 시, 이미 존재하는 파일인 지 확인하기 위함)
        self.json_file_display_list = file_names

        self.json_data_manager.set_target_json_file(None, None)
    
    def save_files(self):
        # 더블 클릭으로 focus된 아이템 release
        self.tree_view.release_double_clicked_target()

        # json_data_manager로 파일 세이브 요청
        self.json_data_manager.save_json_files()

    def rename_file(self):
        # 더블클릭되어 target으로 설정된 파일이 없을 경우, 클릭으로 선택된 파일이 있는 지 검사
        if self.json_data_manager.file_name is None:

            # 선택된 파일이 없을 경우
            if self.selected_items is None:
                    CustomMessageBox.warning(self.parent, "Warning", "No file has been selected.")
                    return
            
            # 선택된 파일 개수가 0일 경우
            if len(self.selected_items) == 0:
                CustomMessageBox.warning(self.parent, "Warning", "No file has been selected.")
                return
            
            # 두 개 이상의 파일이 선택된 경우
            if len(self.selected_items) > 1:
                CustomMessageBox.warning(self.parent, "Warning", "More than one item has been selected.")
                return
            
            old_file_name = self.selected_items[0][0]

        else:
            old_file_name = self.json_data_manager.file_name

        # 유저에게 파일명 입력 요청
        old_file_path = os.path.join(self.directory, old_file_name)
        new_file_name, new_file_path = self.__set_file_name(old_file_name)

        # 파일명 유효성 검사
        if new_file_name is None:
            return
        
        # 이전 파일명과 같을 경우 종료
        if old_file_name == new_file_name:
            return
        
        if new_file_name.endswith(target_filename_extension):
            new_file_path = os.path.join(self.directory, new_file_name)
            
            self.json_data_manager.rename_json_data(old_file_name, new_file_name)
            try:
                # 파일 이름 변경
                os.rename(old_file_path, new_file_path)

                # Release target file
                self.json_data_manager.set_target_json_file(self.directory, None)
                
            except Exception as e:
                CustomMessageBox.critical(self.parent, "Error", f"Failed to rename file: {e}")
                
        else:
            CustomMessageBox.warning(self.parent, "Warning", f"The file name must end with '{target_filename_extension}")

    def refresh_list(self):
        is_data_changed = False

        # json_data_manager에 저장된 모든 데이터에 대한 탐색 수행
        for json_data in self.json_data_manager.data_hist.values():
            # unsaved data (추가 대기) 혹은 hide data (삭제 대기) 데이터가 존재할 경우
            # is_data_changed를 True로 만들고 루프 종료
            for unsaved_data_flag in json_data[1].values():
                if unsaved_data_flag is True:
                    is_data_changed = True
                    break
            for hide_flag in json_data[2].values():
                if hide_flag is True:
                    is_data_changed = True
                    break

        if is_data_changed:
            # 사용자에게 확인 메시지 띄우기
            reply = CustomMessageBox.question(
                self.parent, 
                "File refresh", 
                "You have unsaved data. Would you like to refresh the list?", 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )

            # 사용자가 '예'를 선택한 경우에만 data refresh 진행
            if reply == QMessageBox.Yes:
                self.tree_view.release_double_clicked_target()
                self.json_data_manager.clear()

        else:
            CustomMessageBox.information(self.parent, "Information", "There is no list to refresh.")


    def add_file(self):
        """파일을 리스트 및 디렉토리에 추가하는 메서드"""
        # 기본 파일 이름 설정
        default_file_name = get_current_time()+"_data.h5"

        # Dialog를 통해 file 명과 경로 받아옴
        new_file_name, file_path = self.__set_file_name(default_file_name)

        # 파일명 유효성 검사
        if new_file_name is None or file_path is None:
            return
        
        # 파일명 중복 검사
        if new_file_name in self.json_file_display_list:
            CustomMessageBox.critical(self.parent, "Error", "The file name is duplicated.")
            return

        file_path = os.path.join(self.directory, new_file_name)
        
        # 파일 생성
        try:
            # 딕셔너리를 JSON 형식으로 파일에 저장
            save_dict_to_h5(file_path, {})
            
            # 목록 추가
            self.tree_view.add_item(new_file_name, False, False)

        except Exception as e:
            CustomMessageBox.critical(self.parent, "Error", f"Failed to create the file : {e}")

    def remove_file(self):
        """선택된 파일을 리스트 및 디렉토리에서 삭제하는 메서드"""
        target_items = []

        # 더블클릭되어 target으로 설정된 파일이 없을 경우, 클릭으로 선택된 파일이 있는 지 검사
        if self.json_data_manager.file_name is None:

            # 선택된 파일이 없을 경우
            if self.selected_items is None:
                CustomMessageBox.warning(self.parent, "Warning", "No file has been selected.")
                return
                
            # 선택된 파일의 개수가 0일 경우
            if len(self.selected_items) == 0:
                CustomMessageBox.warning(self.parent, "Warning", "No file has been selected.")
                return
            
            # 파일의 text가 list형태로 나오기 때문에, 첫 번째 인덱스를 사용
            # ex) [[file1.json], [file2.json]]
            for selected_item in self.selected_items:
                target_items.append(selected_item[0])

        else:
            target_items.append(self.json_data_manager.file_name)

        message = "Are you sure you want to delete the selected file?<br>"
        for i, target_item in enumerate(target_items):
            if i == len(target_items)-1:
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
            
            # 선택된 모든 아이템에 대해 작업 수행
            for target_item in target_items:
                
                # 선택된 아이템의 file_name 및 file_path 구성
                file_path = os.path.join(self.directory, target_item)
                
                # 파일 삭제
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
                    self.json_data_manager.remove_json_data(target_item)
                    # 디렉토리 파일 변경으로 TreeView가 업데이트됨 (update 메서드 호출 불필요)

                except Exception as e:
                    CustomMessageBox.critical(self.parent, "File deletion error", f"Failed to delete the file: {e}")
                    
    def __on_file_double_click(self, file_name):
        """파일 리스트에서 항목을 더블 클릭했을 때 동작"""
        
        # 선택된 파일이 없을 경우
        if file_name is None:
            self.json_data_manager.set_target_json_file(None, None)
            return
        
        # 파일명이 잘못된 경우
        if len(file_name) != 1:
            self.json_data_manager.set_target_json_file(None, None)
            return
        
        # json data manager 설정
        self.json_data_manager.set_target_json_file(self.directory, file_name[0])

    def __on_item_clicked(self, selected_items):
        self.selected_items = selected_items
        
    def __set_file_name(self, default_text=""):
        # 파일 이름을 입력받는 다이얼로그 팝업
        file_name, ok = CustomInputDialog.getText(self.parent, "File creation", "Please enter the file name.", text=default_text)

        # 사용자가 입력을 확인하면 파일 이름 설정
        if ok and file_name:
            # 파일 이름에 확장자가 없으면 target_filename_extension 추가
            if not file_name.endswith(target_filename_extension):
                file_name += target_filename_extension
            
            # 파일 경로 설정
            file_path = os.path.join(self.directory, file_name)
            return file_name, file_path
        else:
            # 사용자가 입력을 취소했을 경우 처리
            CustomMessageBox.warning(self, "Warning", "The file name has not been entered.")
            return None, None