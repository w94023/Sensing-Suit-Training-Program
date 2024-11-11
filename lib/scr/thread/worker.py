from .common import *

class BackgroundThreadWorker(QThread):
    progress_changed = pyqtSignal(float)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_running = True  # 스레드 실행 상태 플래그
        self._previous_progress = -1 # 잦은 GUI 업데이트 호출 방지

    def run(self):
        """자식 클래스에서 run 메서드를 구현하도록 남겨둠"""
        raise NotImplementedError("Subclasses should implement this method.")

    def stop(self):
        """스레드 작업을 중단하도록 플래그 설정"""
        self._is_running = False
        
    def update_progress(self, current_progress):
        if int(current_progress) > self._previous_progress:  # 1% 이상 증가 시에만 업데이트
            self.progress_changed.emit(current_progress)
            self._previous_progress = int(current_progress)