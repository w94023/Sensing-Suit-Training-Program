from .common import *
from .worker import *
from PyQt5.QtCore import QCoreApplication

class ProgressDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        # 레이아웃 생성
        self.setWindowTitle(title)
        self.setModal(True) # 부모 창과 상호 작용 차단
        
        # 중도 정지 시 종료할 백그라운드 스레드
        self.worker = None
        
        # 지나친 GUI 업데이트를 방지하기 위해, 이전 값에 비해 1% 이상 상승했을 때만 UI 업데이트
        self.previous_progress = -1

        # 레이아웃 설정
        layout = QVBoxLayout()

        # Progress bar 생성
        self.progress_bar = CustomProgressBar(0, parent=self)

        # "작업 중" 애니메이션 GIF 추가
        self.loading_label = QLabel(self)
        self.movie = QMovie(PyQtAddon.convert_url(os.path.join(icons_directory, "loading_icon.gif")))  # 로딩 애니메이션 GIF 파일 경로
        self.movie.setScaledSize(QSize(40, 40)) # QMovie의 크기를 특정 픽셀 크기로 설정
        self.loading_label.setMovie(self.movie)
        self.movie.start()
        
        # 취소 버튼 추가
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_task)
        self.cancel_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.cancel_button.setStyleSheet(f"""
                                          QPushButton {{
                                              background-color: transparent;
                                              border: 1px solid {PyQtAddon.get_color("content_line_color")};
                                              color: {PyQtAddon.get_color("content_text_color")};
                                              padding: 5px;
                                          }}
                                          QPushButton:hover {{
                                              background-color: {PyQtAddon.get_color("point_color_1")}
                                          }}
                                          """)
        button_layout = QHBoxLayout()
        button_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Preferred, QSizePolicy.Preferred))
        button_layout.addWidget(self.cancel_button)
        button_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Preferred, QSizePolicy.Preferred))
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        
        # 레이아웃에 위젯 추가
        layout.addWidget(self.loading_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.progress_bar)
        layout.addWidget(button_widget, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {PyQtAddon.get_color("background_color")};
                border: none;
            }}
        """)
        
    def set_worker(self, worker):
        if worker is None:
            self.worker = None
            return
        
        if not isinstance(worker, BackgroundThreadWorker):
            print("잘못된 worker 입력입니다")
            worker = None
            return
        
        # 백그라운드 스레드 설정
        self.worker = worker
        
        # update method 연결
        self.worker.progress_changed.connect(self.update_progress)
        
    def start_progress(self):
        """백그라운드 스레드 작업 시작"""
        self.progress_bar.set_value(0)  # ProgressBar 초기화
        self.previous_progress = -1
        self.show()

    def update_progress(self, value):
        """진행 상황을 업데이트"""
        self.progress_bar.set_value(int(value))

    def stop_progress(self):
        self.progress_bar.set_value(100)
        self.accept()
        
    def cancel_task(self):
        # 닫기 버튼 클릭 시 창 닫기 실행
        self.close()
        
    def closeEvent(self, event):
        # 유저가 창을 닫았을 경우, 백그라운드 스레드 강제 중단
        if self.worker is None:
            event.accept()
            return
        
        self.worker.stop()  # 백그라운드 작업 중지 요청
        self.worker.wait()  # 스레드가 완전히 종료될 때까지 대기
        event.accept()      # 창을 닫음