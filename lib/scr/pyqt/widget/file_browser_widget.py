from ....pyqt_base import *
from ....ui_common import *

class CustomTreeView(QTreeView):
    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.callback = callback
                    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                self.callback(file_path)
                
        else:
            event.ignore()  

class CustomFileBorwser(QWidget):
    def __init__(self, on_path_changed):
        super().__init__()

        self.path = ""
        self.on_path_changed = on_path_changed
        self.setStyleSheet(f"""
                           QWidget {{
                             margin: 0px;
                             padding: 0px;
                             background-color: none;
                             border-top:1px solid {PyQtAddon.get_color("content_line_color")}; 
                             border-bottom:1px solid {PyQtAddon.get_color("content_line_color")};
                           }}
                           """)

        # Layout 생성
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 전체적인 border line 생성을 위한 QWidget 생성
        sub_widget = QWidget()
        sub_layout = QHBoxLayout()
        sub_widget.setLayout(sub_layout)
        main_layout.addWidget(sub_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Icon 생성
        svg_widget = QSvgWidget(PyQtAddon.convert_url(os.path.join(icons_directory, "current_directory_icon.svg")))
        svg_widget.setFixedSize(30, 30)
        svg_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        svg_widget.setStyleSheet("border:none")
        sub_layout.addWidget(svg_widget)

        # Directory showing label 생성
        self.directory_label = QLabel("...")
        self.directory_label.setStyleSheet(f"""
                                           color:{PyQtAddon.get_color("content_text_color")}; 
                                           font-family:'{PyQtAddon.text_font}'; 
                                           border:none;
                                           """)
        self.directory_label.setMinimumSize(0, 30)
        self.directory_label.setMaximumSize(16777215, 30)

        # QLabel의 크기 조정 정책 설정 (크기 제한을 없앰)
        self.directory_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        sub_layout.addWidget(self.directory_label)

        # Directory search button 생성
        directory_search_button = QPushButton()
        directory_search_button.setFixedSize(30, 30)
        directory_search_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        directory_search_button.clicked.connect(self.open_file_dialog)
        directory_search_button.setStyleSheet(f"""
                                              QPushButton {{
                                              border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "directory_search_icon.svg"))}"); /* 기본 아이콘 */
                                              }}
                                              QPushButton:hover {{
                                              border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "directory_search_icon_hover.svg"))}"); /* 기본 아이콘 */
                                              }}
                                              QPushButton:pressed {{
                                              border-image: url("{PyQtAddon.convert_url(os.path.join(icons_directory, "directory_search_icon_pressed.svg"))}"); /* 기본 아이콘 */
                                              }}
                                              """)
        sub_layout.addWidget(directory_search_button)
        sub_layout.setContentsMargins(0, 0, 0, 0)

        # QTimer를 사용하여 addDockWidget 이후 크기 확인
        QTimer.singleShot(0, self.check_label_width)

    def set_ellipsized_text(self, text):
        """QLabel의 텍스트가 너무 길면 ...으로 표시되도록 설정"""
        # QLabel의 폰트로 QFontMetrics 객체 생성
        metrics = QFontMetrics(self.directory_label.font())

        # QLabel의 너비에 맞춰 텍스트 자르기 (엘리시스 추가)
        elided_text = metrics.elidedText(text, Qt.ElideRight, self.directory_label.width())

        # 잘라낸 텍스트를 QLabel에 설정
        self.directory_label.setText(elided_text)

    def resizeEvent(self, event):
        """윈도우 크기가 조절되면 텍스트를 다시 자름"""
        self.set_ellipsized_text(self.path)
        super().resizeEvent(event)
    
    def set_directory(self, path):
        # label의 text만 변경
        self.path = path
        self.set_ellipsized_text(self.path)

    def check_label_width(self):
        """DockWidget 추가 이후 QLabel의 크기 확인"""
        self.set_ellipsized_text(self.path)

    def open_file_dialog(self):
        """파일 탐색기를 열어 사용자가 선택한 경로를 출력"""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")

        if directory:
            self.set_directory(directory)
            if self.on_path_changed:
                self.on_path_changed(self.path)
                
class CustomFileSystemWidget(QWidget):
    class CustomModel(QStandardItemModel):
        def __init__(self, directory):
            super().__init__()
            self.directory = directory
            
        def mimeData(self, indexes):
            mime_data = QMimeData()
            if indexes:
                # 드래그된 항목의 사용자 정의 "이름" 데이터를 MimeData에 저장
                item = self.itemFromIndex(indexes[0])

                # 파일 명 Text로 저장
                mime_data.setText(item.text())
                
                # 파일 경로 Url로 저장
                mime_data.setUrls([QUrl.fromLocalFile(os.path.join(self.directory, item.text()))])

            return mime_data
    
    def __init__(self, root_dir):
        super().__init__()

        # 현재 디렉토리 설정
        self.current_directory = root_dir

        # QFileSystemWatcher 설정 (파일 시스템 변화 감시)
        self.watcher = QFileSystemWatcher([self.current_directory])
        self.watcher.directoryChanged.connect(self.on_directory_changed)

        # QVBoxLayout 생성
        layout = QVBoxLayout()

        # File browser 생성
        self.file_browser = CustomFileBorwser(self.on_path_changed)
        layout.addWidget(self.file_browser)

        # QStandardItemModel 생성
        self.model = self.CustomModel(self.current_directory)
        self.model.setHorizontalHeaderLabels(['Files and Folders'])

        # 파일 및 폴더 추가
        self.add_items(self.model, self.current_directory)

        # QTreeView 생성
        self.tree = CustomTreeView(self.on_drag_and_drop_event)
        self.tree.setModel(self.model)
        self.tree.setItemsExpandable(False)  # 항목 확장 불가
        self.tree.setRootIsDecorated(False)  # 트리 루트 장식 없애기

        # 헤더 숨기기 (열 이름 숨기기)
        self.tree.setHeaderHidden(True)
        
        # 파일명만 보이도록 다른 열 숨기기 (파일 이름은 0번 열)
        self.tree.setColumnHidden(1, True)  # 파일 크기 숨기기
        self.tree.setColumnHidden(2, True)  # 파일 종류 숨기기
        self.tree.setColumnHidden(3, True)  # 수정 날짜 숨기기

        # 드래그 앤 드롭 설정
        self.tree.setAcceptDrops(True)
        self.tree.setDragEnabled(True)
        self.tree.setDropIndicatorShown(True)

        # QTreeView에서 더블 클릭 시 항목을 처리
        self.tree.doubleClicked.connect(self.on_item_double_clicked)

        self.tree.setStyleSheet(f"""
                                QTreeView {{
                                    background-color: {PyQtAddon.get_color("background_color")};  /* 배경색 검정 */
                                    color: {PyQtAddon.get_color("title_text_color")};
                                    font-family:{PyQtAddon.text_font};
                                    border:none;
                                }}
                                QTreeView::item {{
                                    background-color: {PyQtAddon.get_color("background_color")};  /* 각 항목의 배경색 검정 */
                                    color: {PyQtAddon.get_color("content_text_color")};  /* 각 항목의 텍스트 색상 흰색 */
                                    font-family:{PyQtAddon.text_font};
                                }}
                                QTreeView::item:hover {{
                                    background-color: {PyQtAddon.get_color("content_hover_color")};
                                }}
                                QTreeView::item:selected {{
                                    background-color: {PyQtAddon.get_color("content_hover_color")};
                                }}
                                """
                                +PyQtAddon.vertical_scrollbar_style
                                +PyQtAddon.horizontal_scrollbar_style)

        # QVBoxLayout에 QTreeView 추가
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.setStyleSheet("QWidget { margin: 0px; padding: 0px; background-color: none;}")

    def add_items(self, parent_item, directory):
        # 파일 브라우져의 경로 수정 
        self.file_browser.set_directory(self.current_directory)
        
        # 모델의 경로 수정
        self.model.directory = self.current_directory

        """특정 디렉토리의 파일 및 폴더를 트리 뷰에 추가"""
        # 상위 디렉토리 경로 계산
        parent_directory = os.path.abspath(os.path.join(self.current_directory, ".."))

        # 상위 디렉토리가 존재할 경우 .. 항목 추가
        if os.path.isdir(parent_directory) and parent_directory != "C:\\":
            # 가장 위에 .. 항목 추가 (상위 디렉토리 이동)
            parent_directory_selector = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "folder_directory_icon.svg"))), '..')
            parent_directory_selector.setEditable(False)
            parent_item.appendRow(parent_directory_selector)

        # 디렉토리 목록과 파일 목록을 분리
        folders = []
        files = []
        for item_name in sorted(os.listdir(directory)):
            item_path = os.path.join(directory, item_name)
            if os.path.isdir(item_path):
                folders.append(item_name)
            else:
                files.append(item_name)

        # 폴더부터 먼저 추가
        for folder in folders:
            folder_item = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "folder_icon.svg"))), folder)
            folder_item.setEditable(False)
            parent_item.appendRow(folder_item)

        # 파일을 나중에 추가
        for file in files:
            if file.endswith('.csv'):
                file_item = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "file_csv_icon.svg"))), file)
            else:
                file_item = QStandardItem(QIcon(PyQtAddon.convert_url(os.path.join(icons_directory, "file_normal_icon.svg"))), file)
            file_item.setEditable(False)
            parent_item.appendRow(file_item)

    def on_item_double_clicked(self, index):
        """더블 클릭 시 .. 항목을 처리하여 상위 디렉토리로 이동"""
        selected_item = self.model.itemFromIndex(index)
        if selected_item.text() == '..':
            # 상위 디렉토리 경로 계산
            parent_directory = os.path.abspath(os.path.join(self.current_directory, ".."))

            # 상위 디렉토리가 존재하는지 확인
            if os.path.isdir(parent_directory):
                # 상위 디렉토리로 이동
                self.current_directory = parent_directory
                self.model.clear()  # 모델을 초기화
                self.add_items(self.model, self.current_directory)  # 상위 디렉토리 내용 추가)

        else:
            # 선택된 디렉토리로 이동
            clicked_path = os.path.join(self.current_directory, selected_item.text())
            if os.path.isdir(clicked_path):
                self.current_directory = clicked_path
                self.model.clear()  # 모델을 초기화
                self.add_items(self.model, self.current_directory)  # 새로운 디렉토리 내용 추가

        # QFileSystemWatcher에 새로운 경로 등록
        self.watcher.removePaths(self.watcher.directories())  # 이전 경로 제거
        self.watcher.addPath(self.current_directory)  # 새 경로 추가

    def on_directory_changed(self, path):
        """감시 중인 디렉토리에서 변경이 발생할 때 호출"""
        self.model.clear()  # 모델을 초기화
        self.add_items(self.model, self.current_directory)  # 현재 디렉토리 내용 업데이트

    def on_drag_and_drop_event(self, file_path):
        # 드랍된 파일의 상위 경로 추출
        parent_directory = os.path.abspath(os.path.join(file_path, ".."))
        self.current_directory = parent_directory
        self.model.clear()  # 모델을 초기화
        self.add_items(self.model, self.current_directory)  # 현재 디렉토리 내용 업데이트

    def on_path_changed(self, file_path):
        self.current_directory = file_path
        self.model.clear()
        self.add_items(self.model, self.current_directory)