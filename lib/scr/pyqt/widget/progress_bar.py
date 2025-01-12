from ....pyqt_base import *
from ....ui_common import *

class CustomProgressBar(QWidget):
    def __init__(self, header_width, parent=None):
        super().__init__(parent)
        
        # Layout 설정
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # header 생성
        # self.header = QLabel()
        # self.header.setText("")
        # self.header.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # self.header.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.header.setFixedSize(header_width, 20)
        # self.header.setStyleSheet(f"""
        #                           QLabel {{
        #                               background-color:{PyQtAddon.get_color("background_color")};
        #                               color:{PyQtAddon.get_color("content_text_color")};
        #                               font-family:{PyQtAddon.text_font};
        #                               }}""")
        # layout.addWidget(self.header)
        
        # ProgressBar 생성
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progress_bar.setFixedSize(0, 10)
        self.progress_bar.setMinimumSize(100, 10)
        self.progress_bar.setMaximumSize(16777215, 10)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet(f"""
                                        QProgressBar {{
                                            border-top:1px solid {PyQtAddon.get_color("line_color")};
                                            border-bottom:1px solid {PyQtAddon.get_color("line_color")};
                                            border-left:none;
                                            border-right:none;
                                            border-radius:0px;
                                            padding-top:2px;
                                            padding-bottom:2px;
                                            background-color:{PyQtAddon.get_color("background_color")};
                                            }}
                                            
                                        QProgressBar::chunk {{
                                            background-color:{PyQtAddon.get_color("line_color")};
                                            width:2.15px;
                                            margin:0.5px;
                                            }}
                                        """)
        layout.addWidget(self.progress_bar)
        
        # ProgressBar label 생성 (진행도 text로 표시)
        self.progress_label = QLabel()
        self.progress_label.setText("0%")
        # self.progress_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.progress_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.progress_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.progress_label.setFixedSize(40, 20)
        self.progress_label.setStyleSheet(f"""
                                          QLabel {{
                                              background-color:{PyQtAddon.get_color("background_color")};
                                              color:{PyQtAddon.get_color("content_text_color")};
                                              font-family:{PyQtAddon.text_font};
                                              }}""")
        layout.addWidget(self.progress_label, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Widget 그래픽 설정
        self.setStyleSheet("QWidget { margin: 0px; padding: 0px; background-color: none; }")

    def set_header(self, header):
        self.header.setText(header)

    def set_value(self, value):
        int_value = int(value)
        self.progress_bar.setValue(int_value)
        self.progress_label.setText(f"{int_value}%")
        self.progress_label.repaint()  # 강제로 다시 그리기