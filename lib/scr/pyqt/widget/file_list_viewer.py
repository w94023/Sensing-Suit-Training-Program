from ....pyqt_base import *
from ....ui_common import *
from .__base__ import *

from .tree_view import CustomDataTreeView
from .message_box import CustomMessageBox
from .input_dialog import CustomInputDialog

target_filename_extension = '.h5'

class FileListViewer(QWidget):
    def __init__(self, file_directory, parent=None):
        self.parent = parent
        super().__init__(self.parent)
        
        # 디렉토리 설정
        self.directory = file_directory

        # QFileSystemWatcher 설정 (파일 시스템 변화 감시)
        self.watcher = QFileSystemWatcher([self.directory])
        self.watcher.directoryChanged.connect(self.update_list)
        
        # List window에서 표시 중인 파일 목록
        self.file_display_list = []
        self.file_unsaved_flags = {}
        
        # 현재 선택된 파일
        self.target_item = None # 더블 클릭 되어 선택된 항목
        self.selected_items = None # 클릭으로 선택한 항목
        
        # 이벤트 생성
        self.on_target_changed    = CustomEventHandler()
        self.on_file_removed      = CustomEventHandler()
        self.on_refresh_requested = CustomEventHandler()
        self.on_save_requested    = CustomEventHandler()
        self.on_file_renamed      = CustomEventHandler()
        
        # UI 초기화
        self.__init_ui()

        # 파일 리스트 초기화
        self.update_list()

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
        
    def update_list(self):
        """디렉토리의 .json 파일만 불러와 리스트에 추가"""
        # 파일 목록 초기화
        file_names = []
        unsaved_file_flag = []

        # Directory에 존재하는 파일 읽어오기
        for file_name in os.listdir(self.directory):

            # 파일인지 확인하고, 확장자가 target_filename_extension 인지 확인
            if os.path.isfile(os.path.join(self.directory, file_name)) and file_name.endswith(target_filename_extension):
                
                # JSON 파일일 경우, 목록에 추가
                file_names.append(file_name)
                
                if file_name in self.file_unsaved_flags.keys():
                    unsaved_file_flag.append(self.file_unsaved_flags[file_name])

                else:
                    self.file_unsaved_flags[file_name] = False
                    unsaved_file_flag.append(False)
                    
        # TreeView에 item 추가
        self.tree_view.add_items_without_selected_flags(file_names, unsaved_file_flag)

        # 인스턴스 데이터로 저장
        # (add file 메서드 호출 시, 이미 존재하는 파일인 지 확인하기 위함)
        self.file_display_list = file_names
        
        # target 파일이 삭제되거나 이동되어 조회된 파일 내에 없을 경우
        # target file release 후 이벤트 호출
        if self.target_item not in file_names:
            self.__set_target_file(None)
        
    def __set_target_file(self, file_name):
        self.target_item = file_name
        self.on_target_changed(file_name)
        
    def __on_item_clicked(self, selected_items):
        if selected_items is None:
            self.selected_items = None
            return

        if len(selected_items) == 0:
            self.selected_items = None
            return
        
        self.selected_items = selected_items
        
    def __on_file_double_click(self, selected_item):
        if selected_item is None:
            self.__set_target_file(None)
            return
        
        if len(selected_item) == 0:
            self.__set_target_file(None)
            return
        
        self.__set_target_file(selected_item[0])
                
    def save_files(self):
        self.on_save_requested()

    def rename_file(self):
        # 더블클릭되어 target으로 설정된 파일이 없을 경우, 클릭으로 선택된 파일이 있는 지 검사
        if self.target_item is None:

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
            old_file_name = self.target_item

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
            
            # rename 이벤트 호출
            self.on_file_renamed(old_file_name, old_file_path, new_file_name, new_file_path)
            
            try:
                # 새로운 파일명으로 현재 target file name 변경
                if self.target_item == old_file_name:
                    self.target_item = new_file_name

                # 파일 이름 변경
                os.rename(old_file_path, new_file_path)

                # unsaved file flag 변경
                if old_file_name in self.file_unsaved_flags.keys():
                    unsaved_flag = self.file_unsaved_flags[old_file_name]
                    self.file_unsaved_flags.pop(old_file_name)
                    self.file_unsaved_flags[new_file_name] = unsaved_flag

                # tree_view 리스트 업데이트
                self.update_list()

                # 변경 후 항목으로 tree_view 포커스 변경
                self.tree_view.set_item_focus(new_file_name)
                
                # 이벤트 호출
                if self.target_item == new_file_name:
                    self.on_target_changed(new_file_name)
                
            except Exception as e:
                CustomMessageBox.critical(self.parent, "Error", f"Failed to rename file: {e}")
                
        else:
            CustomMessageBox.warning(self.parent, "Warning", f"The file name must end with '{target_filename_extension}")

    def refresh_list(self):
        self.on_refresh_requested()

    def add_file(self):
        """파일을 리스트 및 디렉토리에 추가하는 메서드"""
        # 기본 파일 이름 설정
        default_file_name = get_current_time()+"_data"+target_filename_extension

        # Dialog를 통해 file 명과 경로 받아옴
        new_file_name, file_path = self.__set_file_name(default_file_name)

        # 파일명 유효성 검사
        if new_file_name is None or file_path is None:
            return
        
        # 파일명 중복 검사
        if new_file_name in self.file_display_list:
            CustomMessageBox.critical(self.parent, "Error", "The file name is duplicated.")
            return

        file_path = os.path.join(self.directory, new_file_name)
        
        # 파일 생성
        try:
            # 딕셔너리를 target extension 형식으로 파일에 저장
            export_dict_data(file_path, {}, target_filename_extension)
            
            # 목록 추가
            self.tree_view.add_item(new_file_name, False, False)

        except Exception as e:
            CustomMessageBox.critical(self.parent, "Error", f"Failed to create the file : {e}")

    def remove_file(self):
        """선택된 파일을 리스트 및 디렉토리에서 삭제하는 메서드"""
        target_items = []
        
        # 클릭으로 선택된 파일이 있는 지 검사
        if self.selected_items is None:
            
            # 더블 클릭으로 선택된 파일이 없을 경우
            if self.target_item is None:
                CustomMessageBox.warning(self.parent, "Warning", "No file has been selected.")
                return
            
            # 더블 클릭으로 선택된 파일이 있는 경우
            target_items.append(self.target_item)
            
        else:
            # 파일의 text가 list형태로 나오기 때문에, 첫 번째 인덱스를 사용
            # ex) [[file1.json], [file2.json]]
            for item in self.selected_items:
                target_items.append(item[0])
                
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
                
                # 삭제 대상 항목이 현재 더블 클릭으로 선택된 아이템일 경우
                if target_item == self.target_item:
                    self.__set_target_file(None) # target file release
                
                # 선택된 아이템의 file_name 및 file_path 구성
                file_path = os.path.join(self.directory, target_item)
                
                # 파일 삭제
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
                        self.on_file_removed(target_item)
                        
                    # 디렉토리 파일 변경으로 TreeView가 업데이트됨 (update 메서드 호출 불필요)

                except Exception as e:
                    CustomMessageBox.critical(self.parent, "File deletion error", f"Failed to delete the file: {e}")
                    
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