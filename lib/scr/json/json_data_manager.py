from .common import *
import copy

class SaveThread(BackgroundThreadWorker):
    # 작업 완료 시그널
    # bool: data load 성공 여부
    # str: target file path
    # Exception: 오류
    save_finished = pyqtSignal(bool, Exception)
    
    def __init__(self, data_hist, parent=None):
        super().__init__(parent)

        self.data_hist = data_hist

    def run(self):
        # data_hist에서, unsaved_data_flag (추가 대기) 및 hide_data_flag (삭제 대기)가 있는 경우에만 저장
        count = 0
        total_count = len(self.data_hist)
        for data in self.data_hist.values():
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
                    save_dict_to_json(data[3], data[0])
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

    def __init__(self, directory, target_file_name, parent=None):
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

    def run(self):
        """백그라운드 스레드에서 JSON 파일에서 데이터 로드"""
        
        # 파일이 JSON 파일인지 확인
        if self.target_file_name.endswith(".json"):
            # 파일 경로 구성
            file_path = os.path.join(self.directory, self.target_file_name)  
            
            self.update_progress(5)
            
            try:
                # JSON 파일에서 딕셔너리 불러오기
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    data_dict = {}
                    
                    self.update_progress(10)

                    # 딕셔너리 요소 순회하면서 dataframe 복원
                    count = 0
                    total_count = len(data)
                    for key, value in data.items():
                        # 데이터프레임으로 변환
                        df = pd.DataFrame(value)

                        # 인덱스를 int로 변환
                        df.index = df.index.astype(int)
                        data_dict[key] = df
                        
                        count += 1
                        self.update_progress(count/total_count*90 + 10)

                    self.load_finished.emit(True, file_path, self.target_file_name, data_dict, Exception())

            except Exception as e:
                self.load_finished.emit(False, file_path, self.target_file_name, {}, e)
                
        else:
            self.load_finished.emit(False, file_path, self.target_file_name, {}, Exception("The file is in an incorrect format."))
                
class JSONDataManager():     
    def __init__(self, parent=None):
        """
        현재 선택된 JSON file 및 내부 데이터의 save, load 관리
        
        Args:
            parent (QWidget): Loading widget 표시할 부모 객체 (QMainWindow). Default to None
        """
        
        # 부모 객체 저장
        self.parent = parent
        
        # 스레드 관리
        self.data_load_thread = None
        self.data_save_thread = None
        
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
        self.on_target_file_changed = CustomEventHandler() 
        """Args:
            (str): file_name 
            (list of pd.DataFrame): file_data
            (list of bool): unsaved_data_flag
            (list of bool): hide_data_lfag
        """

    def __set_target_file_data(self, data, unsaved_data_flag, hide_data_flag):
        self.file_data = copy.deepcopy(data)
        self.file_unsaved_data_flag = copy.deepcopy(unsaved_data_flag)
        self.file_hide_data_flag = copy.deepcopy(hide_data_flag)

        self.__on_target_file_data_changed()

    def __on_target_file_data_changed(self):
        # Target file의 data 변경 시, 이벤트를 호출하는 메서드
        # hist에 저장하지 않음
        self.on_target_file_changed(self.file_name, 
                                    copy.deepcopy(self.file_data),
                                    copy.deepcopy(self.file_unsaved_data_flag), 
                                    copy.deepcopy(self.file_hide_data_flag))
        
    def __clear_target_json_file_data(self):
        # Target file data 초기화
        self.file_name = None
        self.file_data = None
        self.file_unsaved_data_flag.clear()
        self.file_hide_data_flag.clear()
        self.file_path = None

        # 이벤트 호출
        self.__on_target_file_data_changed()

    def set_target_json_file(self, file_directory, file_name):
        """JSON target 파일 설정

        Args:
            file_directory (str): JSON 파일의 디렉토리
            file_name (str): JSON 파일 명
        """

        # None이 주어졌을 경우, 인스턴스 target json file 데이터 clear 실행
        if file_directory is None or file_name is None:
            self.__clear_target_json_file_data()

        # None이 아닐 경우, file_name 및 file_path 저장
        else:
            self.file_name = file_name
            self.file_path = os.path.join(file_directory, file_name)

            # 데이터 로드 시도
            self.__load_json_file(file_directory, self.file_name)
        
    def __load_json_file(self, file_directory, file_name):
        """설정된 JSON 파일 디렉토리 및 파일명에서 데이터 load"""

        if file_directory is None or file_name is None:
            CustomMessageBox.critical(self.parent, "Error", "The target JSON file has not been set.")
            return
        
        if self.data_load_thread is not None:
            CustomMessageBox.critical(self.parent, "Error", "The previous data load task has not been completed.")
            return
        
        # Load 요청한 JSON 파일의 데이터가 이미 인스턴스 데이터에 저장되어 있을 경우, 새로 load하지 않음
        if file_name in self.data_hist.keys():
            self.__set_target_file_data(self.data_hist[file_name][0],
                                        self.data_hist[file_name][1],
                                        self.data_hist[file_name][2])
        
        # Load 요청한 JSON 파일이 인스턴스 데이터에 없을 경우
        else:
            # 작업 시작 window 표시
            # self.loading_dialog.on_task_started()
            self.loading_dialog.start_progress()
            
            # 백그라운드 스레드에서 data load 작업 수행
            self.data_load_thread = LoadThread(file_directory, file_name, self.parent)
            self.data_load_thread.load_finished.connect(self.__on_json_data_load_finished)
            self.loading_dialog.set_worker(self.data_load_thread) # 백그라운드 스레드 설정
            self.data_load_thread.start()
            
    def __on_json_data_load_finished(self, is_succeed, file_path, file_name, data_dict, exception):
        """JSON 파일 데이터 로드 완료 시 호출되는 메서드

        Args:
            is_succeed (bool): 데이터 로드 성공 여부
            file_name (str): target JSON file name
            data_dict (dict of pd.DataFrame): JSON 파일에서 로드한 데이터
            exception (Exception): 데이터 로드 실패 시 발생한 오류
        """

        unsaved_data_flag = {}
        hide_flag = {}
        if is_succeed:
            
            # 데이터로부터 key 추출
            keys = data_dict.keys()
            
            for key in keys:
                # unsaved flag 및 hide flag 모두 False로 설정
                # JSON file 에서 데이터 불러온 결과이기 때문에,
                # JSON file에 저장되지 않았거나, JSON file에서 삭제되지 않은 데이터는 아직 없음
                unsaved_data_flag[key] = False
                hide_flag[key] = False
            
            self.file_path = file_path

            self.data_hist[self.file_name] = copy.deepcopy([
                copy.deepcopy(data_dict),
                copy.deepcopy(unsaved_data_flag),
                copy.deepcopy(hide_flag),
                self.file_path
            ])
            self.__set_target_file_data(data_dict, unsaved_data_flag, hide_flag)
                                
        else:
            self.__set_target_file_data(None, None, None)
            CustomMessageBox.critical(self.parent, "Error", f"Error to load {file_name} : {exception}")
            
        self.loading_dialog.stop_progress()
        self.data_load_thread = None
        self.loading_dialog.set_worker(self.data_load_thread) # 백그라운드 스레드 설정
        
    def rename_json_data(self, old_file_name, new_file_name):
        # 데이터 이전   
        if old_file_name in self.data_hist.keys():
            old_data = copy.deepcopy(self.data_hist[old_file_name])
            self.data_hist.pop(old_file_name)
            self.data_hist[new_file_name] = old_data
            
            if old_file_name == self.file_name:
                self.file_name = new_file_name
                self.__set_target_file_data(self.data_hist[new_file_name][0],
                                            self.data_hist[new_file_name][1],
                                            self.data_hist[new_file_name][2])
                
    def remove_json_data(self, file_name):
        if file_name in self.data_hist.keys():
            self.data_hist.pop(file_name)
        
    def add_data_to_target_json_file(self, key, df):
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
    
    def remove_data_from_target_json_file(self, keys):
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
        
    def clear(self):
        # 인스턴스 데이터 초기화
        self.data_hist.clear()
        self.__clear_target_json_file_data()

    def save_json_files(self):
        if self.data_save_thread is not None:
            CustomMessageBox.critical(self.parent, "Error", "The previous data save task has not been completed.")
            return
        
        # 작업 시작 window 표시
        self.saving_dialog.start_progress()
        
        # 백그라운드 스레드에서 data load 작업 수행
        self.data_save_thread = SaveThread(self.data_hist, self.parent)
        self.data_save_thread.save_finished.connect(self.__on_save_finished)
        self.saving_dialog.set_worker(self.data_save_thread) # 백그라운드 스레드 연결
        self.data_save_thread.start()

    def __on_save_finished(self, is_succeed, exception):
        self.__on_target_file_data_changed()
        self.saving_dialog.stop_progress()

        if is_succeed:
            CustomMessageBox.information(self.parent, "Information", "Data has been saved successfully.")
        else:
            CustomMessageBox.critical(self.parent, "Error", "Failed to save data : " + str(exception))
            
        self.data_save_thread = None
        self.saving_dialog.set_worker(self.data_save_thread) # 백그라운드 스레드 연결

