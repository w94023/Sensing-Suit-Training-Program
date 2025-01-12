from .common import *
import copy

from ..pyqt.widget import (CustomMessageBox)

class SaveThread(BackgroundThreadWorker):
    # 작업 완료 시그널
    # bool: data load 성공 여부
    # str: target file path
    # Exception: 오류
    save_finished = pyqtSignal(bool, Exception)
    target_file_changed = pyqtSignal(str, dict, dict, dict)
    
    def __init__(self, data_hist, target_file_name, target_filename_extension, parent=None):
        super().__init__(parent)

        self.data_hist = data_hist
        self.target_file_name = target_file_name
        self.target_filename_extension = target_filename_extension

    def run(self):
        # data_hist에서, unsaved_data_flag (추가 대기) 및 hide_data_flag (삭제 대기)가 있는 경우에만 저장
        count = 0
        total_count = len(self.data_hist)
        for file_name, data in self.data_hist.items():
            # data[0]: file_data
            # data[1]: unsaved_data_flag
            # data[2]: hide_data_flag
            # data[3]: file_path

            # file_data의 key 목록 불러오기
            data_keys = data[0].keys()

            # hide_data_flag가 True인 경우, file_data에서 해당 데이터 삭제
            delete_target_keys = []
            for data_key in data_keys:
                if data[2][data_key] is True:
                    delete_target_keys.append(data_key)

            for key in delete_target_keys:
                del data[0][key]
                del data[1][key]
                del data[2][key]
                    
            # unsaved_data_flag가 True일 경우, 해당 데이터 저장
            do_save = False
            for data_key in data_keys:
                if data[1][data_key] is True:
                    do_save = True
                    data[1][data_key] = False

            if do_save:
                try:
                    # 타겟 파일 변경 후 이벤트 호출
                    if file_name == self.target_file_name:
                        self.target_file_changed.emit(file_name, data[0], data[1], data[2])

                    export_dict_data(data[3], data[0], self.target_filename_extension)
                    count += 1
                    self.update_progress(count/total_count*100)
                    
                except Exception as e:
                    self.save_finished.emit(False, e)
                    return

        self.save_finished.emit(True, Exception())
                        
class LoadThread(BackgroundThreadWorker):
    # 작업 완료 시그널
    # bool: data load 성공 여부
    # str: target file path
    # str: target file path
    # dict: load된 데이터 (dictionary of pd.DataFrame)
    # Exception: 오류
    load_finished = pyqtSignal(bool, str, str, dict, Exception)

    def __init__(self, directory, target_file_name, target_filename_extension, key_length, key_splitter, parent=None):
        """백그라운드 스레드에서 JSON 데이터 로드하기 위한 클래스

        Args:
            directory (str): target file directory
            target_file_name (str): target file name
            parent (QWidget, optional): 부모 위젯 (QMainWindow). Defaults to None.
        """
        super().__init__(parent)
        
        # 매개 변수 저장
        self.directory = directory
        self.target_file_name = target_file_name
        self.target_filename_extension = target_filename_extension
        self.key_length = key_length
        self.key_splitter = key_splitter
        
    def __check_data_name_validity(self, key):
        # load된 dictionary 데이터의 key의 길이가 일치하는 지 확인
        # ex. key_splitter : '-', key_length : 3
        # > "AA-marker-raw" : O, "AA-marker-raw-1" : X
        if len(key.split(self.key_splitter)) == self.key_length:
            return True
        else:
            return False
    
    def run(self):
        """백그라운드 스레드에서 JSON 파일에서 데이터 로드"""
        
        # 확장자 확인
        if self.target_file_name.endswith(self.target_filename_extension):
            
            # 파일 경로 구성
            file_path = os.path.join(self.directory, self.target_file_name)  

            self.update_progress(5)
        
            try:
                # 파일에서 딕셔너리 불러오기
                data = import_dict_data(file_path, self.target_filename_extension)
                data_dict = {}

                self.update_progress(10)
                
                # 딕셔너리 요소 순회하면서 dataframe 복원
                count = 0
                total_count = len(data)
                for key, value in data.items():
                    # key가 유효하지 않을 경우 뛰어넘음
                    if not self.__check_data_name_validity(key):
                        continue
                    
                    # 데이터프레임으로 변환
                    df = pd.DataFrame(value)

                    # 인덱스를 int로 변환
                    df.index = df.index.astype(int)
                    data_dict[key] = df

                    count += 1
                    self.update_progress(count/total_count*90 + 10)

                # self.__on_file_loaded(file_name, file_path, data_dict)
                self.load_finished.emit(True, self.target_file_name, file_path, data_dict, Exception())
      
            except Exception as e:
                self.load_finished.emit(False, self.target_file_name, file_path, {}, e)
                
        else:
            self.load_finished.emit(False, self.target_file_name, file_path, {}, Exception("The file is in an incorrect format."))
                
class DataHandler():     
    def __init__(self, file_directory, target_filename_extension, key_length, key_splitter, parent=None):
        """
        현재 선택된 JSON file 및 내부 데이터의 save, load 관리
        
        Args:
            parent (QWidget): Loading widget 표시할 부모 객체 (QMainWindow). Default to None
        """
        
        # 데이터 저장 디렉토리 설정
        self.file_directory = file_directory
        
        # 대상 파일 확장자 설정
        self.target_filename_extension = target_filename_extension
        
        # 데이터 키 인식을 위한 파라미터 저장
        self.key_length = key_length # 3
        self.key_splitter = key_splitter # '-'
        
        # 부모 객체 저장
        self.parent = parent
        
        # 스레드 관리
        self.loading_thread = None
        self.saving_thread = None
        
        # 오래 걸리는 작업을 처리하기 위한 dialog 생성
        self.loading_dialog = ProgressDialog("Data loading progress", self.parent)
        self.saving_dialog = ProgressDialog("Data saving progress", self.parent)
        
        # json 데이터 관련
        self.file_name = None            # 현재 작업 대상 파일명
        self.file_data = {}              # 현재 작업 대상 파일 데이터
        self.file_unsaved_data_flag = {} # 현재 작업 대상 파일 데이터 중, json file에는 저장되지 않았으나 추가된 데이터 flag
        self.file_hide_data_flag = {}    # 현재 작업 대상 파일 데이터 중, json file에서는 삭제되지 않았으나 삭제된 데이터 flag
        self.file_path = None            # 현재 작업 대상 파일의 경로
        # 현재까지 작업한 데이터 리스트
        # key : file_name
        # value : list
            # index 0 > data
            # index 1 > unsaved_data_flag
            # index 2 > hide_data_flag
            # index 3 > file path
        self.data_hist = {}
        
        # 이벤트 관리
        self.on_target_data_changed = CustomEventHandler() 
        """Args:
            (str): file_name 
            (list of pd.DataFrame): file_data
            (list of bool): unsaved_data_flag
            (list of bool): hide_data_lfag
        """

    def clear(self):
        self.data_hist.clear()
        
        # Target file data 초기화
        self.file_name = None
        self.file_data = None
        self.file_unsaved_data_flag.clear()
        self.file_hide_data_flag.clear()
        self.file_path = None

        # 이벤트 호출
        self.__on_target_file_data_changed()
                   
    def add_target_file_data(self, file_name):
        if file_name is None:
            # Target file data 초기화
            self.file_name = None
            self.file_data = None
            self.file_unsaved_data_flag.clear()
            self.file_hide_data_flag.clear()
            self.file_path = None
            
            # 이벤트 호출
            self.__on_target_file_data_changed()
            return
        
        if self.loading_thread is not None:
            CustomMessageBox.critical(self.parent, "Error", "The previous data load task has not been completed.")
            return
        
        # 작업 시작 window 표시
        self.loading_dialog.start_progress()
        
        # 백그라운드 스레드에서 data load 작업 수행
        self.loading_thread = LoadThread(self.file_directory, file_name, self.target_filename_extension, self.key_length, self.key_splitter, self.parent)
        self.loading_thread.load_finished.connect(self.__on_file_loaded)
        self.loading_dialog.set_worker(self.loading_thread) # 백그라운드 스레드 설정
        self.loading_thread.start()
  
    def __on_file_loaded(self, is_succeed, file_name, file_path, df, exception):
        if is_succeed:
            # 주어진 파일의 데이터가 이미 인스턴스 데이터에 저장되어 있을 경우, 데이터를 업데이트 하지 않음
            if file_name in self.data_hist.keys():
                self.__set_target_file_data(file_name,
                                            self.data_hist[file_name][0],
                                            self.data_hist[file_name][1],
                                            self.data_hist[file_name][2])
            # 주어진 파일의 데이터가 인스턴스 데이터에 없을 경우, 인스턴스 데이터에 데이터 추가
            else:
                unsaved_data_flag = {}
                hide_data_flag = {}
                for key in df.keys():
                    unsaved_data_flag[key] = False
                    hide_data_flag[key] = False
                    
                self.data_hist[file_name] = copy.deepcopy([
                    copy.deepcopy(df),
                    unsaved_data_flag,
                    hide_data_flag,
                    file_path
                ])
                self.__set_target_file_data(file_name, df, unsaved_data_flag, hide_data_flag)
                self.file_path = file_path
        # file load에 실패한 경우
        else:
            self.__set_target_file_data(None, None, None, None)
            CustomMessageBox.critical(self.parent, "Error", f"Error to load {file_name} : {exception}")

        self.loading_dialog.stop_progress()
        self.loading_thread = None
        self.loading_dialog.set_worker(self.loading_thread)
            
    def __set_target_file_data(self, name, data, unsaved_data_flag, hide_data_flag):
        self.file_name = name
        self.file_data = copy.deepcopy(data)
        self.file_unsaved_data_flag = copy.deepcopy(unsaved_data_flag)
        self.file_hide_data_flag = copy.deepcopy(hide_data_flag)

        self.__on_target_file_data_changed()
        
    def __on_target_file_data_changed(self):
        # Target file의 data 변경 시, 이벤트를 호출하는 메서드
        # hist에 저장하지 않음
        if self.file_name is None:
            self.on_target_data_changed(None, None, None, None)
        else:
            self.on_target_data_changed(self.file_name, 
                                        copy.deepcopy(self.file_data),
                                        copy.deepcopy(self.file_unsaved_data_flag), 
                                        copy.deepcopy(self.file_hide_data_flag))
        return
            
    def remove_file_data(self, file_name):
        # 인스턴스 데이터 내에 요청된 파일 명이 없을 경우, 작업 종료
        if file_name not in self.data_hist.keys():
            return
        
        # 인스턴스 데이터 내에서 데이터 삭제
        self.data_hist.pop(file_name)
        
        # 현재 선택된 파일이 삭제된 경우, target file data 업데이트
        if file_name == self.file_name:
            self.__set_target_file_data(None, None, None, None)
            
    def export_data_hist(self):
        if self.saving_thread is not None:
            CustomMessageBox.critical(self.parent, "Preparation data export error", "The previous data save task has not been completed.")
            return
        
        # 작업 시작 window 표시
        self.saving_dialog.start_progress()
        
        # 백그라운드 스레드에서 data load 작업 수행
        self.saving_thread = SaveThread(self.data_hist, self.file_name, self.target_filename_extension, self.parent)
        self.saving_thread.target_file_changed.connect(self.__set_target_file_data)
        self.saving_thread.save_finished.connect(self.__on_save_finished)
        self.saving_dialog.set_worker(self.saving_thread) # 백그라운드 스레드 연결
        self.saving_thread.start()

    def __on_save_finished(self, is_succeed, exception):
        self.saving_dialog.stop_progress()

        if is_succeed:
            CustomMessageBox.information(self.parent, "Preparation data export information", "Data has been saved successfully.")
        else:
            CustomMessageBox.critical(self.parent, "Preparation data export error", "Failed to save data : " + str(exception))
            
        self.saving_thread = None
        self.saving_dialog.set_worker(self.saving_thread)


    def rename_data(self, old_file_name, old_file_path, new_file_name, new_file_path):
        if old_file_name not in self.data_hist.keys():
            return
        
        old_data = copy.deepcopy(self.data_hist[old_file_name])
        self.data_hist.pop(old_file_name)
        self.data_hist[new_file_name] = old_data
        self.data_hist[new_file_name][3] = new_file_path
            
    def set_target_file(self, file_name):
        
        # release action일 경우
        if file_name is None:
            self.__set_target_file_data(None, None, None, None)
            return
            
        # 인스턴스 데이터 내에 요청된 파일 명이 없을 경우, 작업 종료
        if file_name not in self.data_hist.keys():
            return
        
        self.__set_target_file_data(file_name, self.data_hist[file_name][0], self.data_hist[file_name][1], self.data_hist[file_name][2])
        
    def add_data_to_target_file(self, key, df):
        """Target JSON 파일에 data 추가하는 메서드

        Args:
            key (str): dictionary에 추가할 key
            df (pd.DataFrame): dictionary에 추가할 value
        """
        # 주어진 key를 가진 df가 이미 self.file_data 내에 있을 경우
        if key in self.file_data:
            
            # 주어진 df와 self.file_data 내의 데이터가 일치할 경우
            if self.file_data[key].equals(df):
                
                # 데이터를 갱신하지 않고 작업 종료
                return

            # 주어진 df와 self.file_data 내의 데이터가 일치하지 않을 경우
            else:
                # 데이터를 갱신
                self.file_data[key] = copy.deepcopy(df)
                self.file_unsaved_data_flag[key] = True
                self.file_hide_data_flag[key] = False

                # self.data_hist 갱신
                self.data_hist[self.file_name] = copy.deepcopy([
                    copy.deepcopy(self.file_data),
                    copy.deepcopy(self.file_unsaved_data_flag),
                    copy.deepcopy(self.file_hide_data_flag),
                    self.file_path
                ])

                self.__on_target_file_data_changed()

        # 주어진 key를 가진 df가 self.file_data 내에 없을 경우
        else:
            # 데이터 추가
            self.file_data[key] = copy.deepcopy(df)
            self.file_unsaved_data_flag[key] = True
            self.file_hide_data_flag[key] = False

            # self.data_hist 갱신
            self.data_hist[self.file_name] = copy.deepcopy([
                copy.deepcopy(self.file_data),
                copy.deepcopy(self.file_unsaved_data_flag),
                copy.deepcopy(self.file_hide_data_flag),
                self.file_path
            ])

            self.__on_target_file_data_changed()
            
    def remove_data_from_target_file(self, keys):
        # 주어진 key를 가진 데이터가 self.file_data 내에 있을 경우
        for key in keys:
            if key in self.file_data.keys():
                # 해당 파일을 숨김 처리
                self.file_hide_data_flag[key] = True

        # self.data_hist 갱신
        self.data_hist[self.file_name] = copy.deepcopy([
            copy.deepcopy(self.file_data),
            copy.deepcopy(self.file_unsaved_data_flag),
            copy.deepcopy(self.file_hide_data_flag),
            self.file_path
        ])

        self.__on_target_file_data_changed()