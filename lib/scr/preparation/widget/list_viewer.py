from ..common import *
from .common import *

from ...pyqt.widget import (FileListViewer, CustomMessageBox)

class PreparationDataListViewer(FileListViewer):
    def __init__(self, preparation_data_handler, file_directory, parent=None):
        super().__init__(file_directory, parent)
        
        # 인스턴스 저장
        self.preparation_data_handler = preparation_data_handler
        self.preparation_data_handler.on_target_data_changed += self.__on_target_data_changed
        
        # 이벤트 연결
        self.on_target_changed    += self.__on_target_file_changed
        self.on_file_removed      += self.__on_file_removed
        self.on_refresh_requested += self.__on_refresh_requested
        self.on_save_requested    += self.__on_save_requested
        self.on_file_renamed      += self.__on_file_renamed
        
    def __on_target_data_changed(self, file_name, data, unsaved_flags, hide_flags):
        if file_name is None:
            return
        
        if file_name in self.file_unsaved_flags.keys():
            
            is_unsaved_data_exist = False
            
            for unsaved_flag in unsaved_flags.values():
                if unsaved_flag is True:
                    is_unsaved_data_exist = True
                    break
                
            for hide_flag in hide_flags.values():
                if hide_flag is True:
                    is_unsaved_data_exist = True
                    break
                
            self.file_unsaved_flags[file_name] = is_unsaved_data_exist
        
        self.update_list()
        
    def __on_target_file_changed(self, file_name):
        self.preparation_data_handler.add_target_file_data(file_name)
        
    def __on_file_removed(self, file_name):
        self.preparation_data_handler.remove_file_data(file_name)
        
    def __on_refresh_requested(self):
        # return
        is_data_changed = False

        # json_data_manager에 저장된 모든 데이터에 대한 탐색 수행
        for data in self.preparation_data_handler.data_hist.values():
            # unsaved data (추가 대기) 혹은 hide data (삭제 대기) 데이터가 존재할 경우
            # is_data_changed를 True로 만들고 루프 종료
            for unsaved_data_flag in data[1].values():
                if unsaved_data_flag is True:
                    is_data_changed = True
                    break
            for hide_flag in data[2].values():
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
                # self.tree_view.release_double_clicked_target()
                self.preparation_data_handler.clear()
                CustomMessageBox.information(self.parent, "Information", "Data refreshed.")

                # unsaved flag 초기화
                for file_name in self.file_unsaved_flags.keys():
                    self.file_unsaved_flags[file_name] = False
                self.update_list()

                self.tree_view.release_double_clicked_target()

        else:
            CustomMessageBox.information(self.parent, "Information", "Data refreshed.")
        
    def __on_save_requested(self):
        self.preparation_data_handler.export_data_hist()

        # unsaved flag 초기화
        for file_name in self.file_unsaved_flags.keys():
            self.file_unsaved_flags[file_name] = False
        self.update_list()
        
    def __on_file_renamed(self, old_file_name, old_file_path, new_file_name, new_file_path):
        if old_file_name is None or old_file_path is None or new_file_name is None or new_file_path is None:
            return
        
        self.preparation_data_handler.rename_data(old_file_name, old_file_path, new_file_name, new_file_path)
        
    