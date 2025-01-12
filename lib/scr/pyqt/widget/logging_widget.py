from ....pyqt_base import *
from ....ui_common import *

class CustomLogWorker(QThread):
    update_label = pyqtSignal(str)
    log = ""

    def create_html(self, text):
        html = f'''
        <html>
        <head>
            <style>
                .normal_log {{
                    color: {PyQtAddon.get_color("content_text_color")};
                }}
            </style>
            <style>
                .error_log {{
                    color: {PyQtAddon.get_color("error_text_color")};
                }}
            </style>
        </head>
        <body>
            {text}
        </body>
        </html>
        '''

        return html

    def add_log(self, log):
        if self.log == "":
            self.log += '<span class="normal_log">'+'> '+log+'</span>'
        else:
            self.log += '<br/>'+'<span class="normal_log">'+'> '+log+'</span>'

        self.update_label.emit(self.create_html(self.log))

    def add_error_log(self, log):
        if self.log == "":
            self.log += '<span class="error_log">'+'> '+log+'</span>'
        else:
            self.log += '<br/>'+'<span class="error_log">'+'> '+log+'</span>'

        self.update_label.emit(self.create_html(self.log))

class CustomLogger(QWidget):
    def __init__(self):
        super().__init__()

        # QLabel 추가
        self.log_label = QLabel()
        self.log_label.setStyleSheet(f"""
                                     QLabel {{
                                         border:none;
                                         background-color:{PyQtAddon.get_color("background_color")};
                                         font-family:{PyQtAddon.text_font};
                                     }}
                                     """)
        
        # QScrollArea 생성 및 QLabel 추가
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.log_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
                                  /* ScrollArea 배경색 */
                                  QScrollArea {{
                                      border:none;
                                      background-color:{PyQtAddon.get_color("background_color")};  
                                  }}
                                  """
                                  +PyQtAddon.vertical_scrollbar_style
                                  +PyQtAddon.horizontal_scrollbar_style)
        
        # vertical scrollbar 조절을 위한 인스턴스 저장
        self.vertical_scrollbar = scroll_area.verticalScrollBar()

        # Layout 설정
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(scroll_area)

        # 메인스레드 동작 worker 생성
        self.worker = CustomLogWorker()
        self.worker.update_label.connect(self.update_label_text)
        self.worker.start()

    def update_label_text(self, text):
        self.log_label.setText(text)
        QTimer.singleShot(0, self.update_scrollbar)
        
    def update_scrollbar(self):
        self.vertical_scrollbar.setValue(self.vertical_scrollbar.maximum())