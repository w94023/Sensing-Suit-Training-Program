from ....pyqt_base import *
from ....ui_common import *

class CustomProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        self.setModal(True) # 부모 창과 상호 작용 차단
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)  # 닫기 버튼 비활성화

        # 레이아웃 생성
        layout = QVBoxLayout()

        # "작업 중" 애니메이션 GIF 추가
        self.loading_label = QLabel(self)
        self.movie = QMovie(PyQtAddon.convert_url(os.path.join(icons_directory, "loading_icon.gif")))  # 로딩 애니메이션 GIF 파일 경로
        self.movie.setScaledSize(QSize(40, 40)) # QMovie의 크기를 특정 픽셀 크기로 설정
        self.loading_label.setMovie(self.movie)
        self.movie.start()
        
        # 정보 라벨 추가
        self.info_label = QLabel("The task is in progress. Please wait...", self)
        self.info_label.setAlignment(Qt.AlignCenter)

        # 텍스트 스타일 설정
        self.info_label.setStyleSheet(f"""QLabel {{
                                         background-color: {PyQtAddon.get_color("background_color")};
                                         color: {PyQtAddon.get_color("title_text_color")};
                                         font-family: {PyQtAddon.text_font};
                                         }}""")

        # 레이아웃에 위젯 추가
        layout.addWidget(self.loading_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.setLayout(layout)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {PyQtAddon.get_color("background_color")};
                border: none;
            }}
        """)

    def on_task_started(self):
        self.show()

    def on_task_finished(self):
        # 작업 완료 시 로딩 대화상자 닫기
        self.accept()