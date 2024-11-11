import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer, QDir, QSignalBlocker
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import (QApplication, QLabel, QCalendarWidget, QFrame, QTreeView,
                             QTableWidget, QFileSystemModel, QPlainTextEdit, QToolBar,
                             QWidgetAction, QComboBox, QAction, QSizePolicy, QInputDialog)

import PyQtAds as QtAds

UI_FILE = os.path.join(os.path.dirname(__file__), 'mainwindow.ui')
MainWindowUI, MainWindowBase = uic.loadUiType(UI_FILE)
# MainWindowUI : .ui 파일에 정의된 인터페이스 클래스입니다. 이 클래스는 UI 위젯 및 레이아웃을 정의하는 역할을 합니다.
# MainWindowBase: .ui 파일의 기반 클래스입니다. 주로 PyQt에서 제공하는 QMainWindow나 QDialog와 같은 클래스가 됩니다.

class MainWindow(MainWindowUI, MainWindowBase):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
 
        #########################################################
        #                       기본 설정                       #
        #########################################################
        #  **스플리터(Splitter)**의 리사이징 동작을 설정하는 플래그입니다.
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.OpaqueSplitterResize, True)
        # 도킹 시스템에서 XML 데이터를 압축할지 여부를 설정하는 플래그입니다.
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.XmlCompressionEnabled, False)
        # 현재 포커스가 있는 도킹된 창(또는 위젯)을 강조하는 설정입니다.
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.FocusHighlighting, True)
        # QtAds 라이브러리에서 CDockManager 객체를 생성하는 코드
        self.dock_manager = QtAds.CDockManager(self)
        
        #########################################################
        #                  Set central widget                   #
        #########################################################
        # **QPlainTextEdit**는 PyQt5에서 제공하는 텍스트 입력 필드입니다.
        text_edit = QPlainTextEdit()
        # 플레이스홀더 텍스트를 설정합니다. 플레이스홀더 텍스트는 사용자가 아무것도 입력하지 않았을 때 나타나는 설명 텍스트입니다.
        text_edit.setPlaceholderText("This is the central editor. Enter your text here.")
        # **CDockWidget**은 QtAds에서 제공하는 도킹 가능한 위젯입니다.
        central_dock_widget = QtAds.CDockWidget("CentralWidget")
        # 텍스트 편집기(QPlainTextEdit)가 중앙 도킹 위젯에 추가됩니다.
        central_dock_widget.setWidget(text_edit)
        # 이 줄은 CDockWidget을 중앙 위젯으로 설정하는 과정입니다.
        central_dock_area = self.dock_manager.setCentralWidget(central_dock_widget)
        # central_dock_area에 대해 도킹이 가능한 영역을 설정하는 코드입니다.
        # 중앙 외부의 영역에 도킹할 수 있지만, 중앙 자체에는 도킹할 수 없습니다.
        central_dock_area.setAllowedAreas(QtAds.DockWidgetArea.OuterDockAreas)
        
        #########################################################
        #               Create other dock widgets               #
        #########################################################
        # **QTableWidget**은 표 형태의 데이터를 표시할 수 있는 테이블 위젯입니다.
        table = QTableWidget()
        # 이 줄은 테이블의 열 개수를 설정합니다.
        table.setColumnCount(3)
        # 이 줄은 테이블의 행 개수를 설정합니다.
        table.setRowCount(10)
        # **CDockWidget**은 QtAds에서 제공하는 도킹 가능한 위젯입니다. 이 줄에서는 "Table 1"이라는 이름의 도킹 위젯을 생성합니다.
        table_dock_widget = QtAds.CDockWidget("Table 1")
        # 이 줄에서는 도킹 위젯 table_dock_widget에 table 위젯을 설정합니다. 즉, 도킹 가능한 창 안에 테이블 위젯이 표시됩니다.
        table_dock_widget.setWidget(table)
        # 도킹 위젯이 스스로의 최소 크기 힌트를 기준으로 크기를 조정하도록 설정하는 역할을 합니다.
        table_dock_widget.setMinimumSizeHintMode(QtAds.CDockWidget.MinimumSizeHintFromDockWidget)
        # 도킹 위젯의 크기를 250x150 픽셀로 설정하는 부분입니다. 초기 크기를 수동으로 지정하여 테이블의 크기를 설정합니다.
        table_dock_widget.resize(250, 150)
        # 도킹 위젯의 최소 크기를 설정하는 부분입니다. 이 경우 최소 크기는 200x150 픽셀로 설정됩니다. 도킹 창의 크기를 줄이더라도 이 최소 크기보다 작아질 수 없습니다.
        table_dock_widget.setMinimumSize(200, 150)
        # 도킹 매니저(dock_manager)를 사용하여 table_dock_widget을 왼쪽 도킹 영역(LeftDockWidgetArea)에 추가합니다.
        # 즉, 테이블 도킹 위젯이 왼쪽 영역에 고정되며, 사용자가 창의 다른 영역으로 도킹할 수 있습니다.
        table_area = self.dock_manager.addDockWidget(QtAds.DockWidgetArea.LeftDockWidgetArea, table_dock_widget)
        # 이 줄은 메뉴에 도킹 위젯을 토글할 수 있는 액션을 추가합니다.
        self.menuView.addAction(table_dock_widget.toggleViewAction())
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setRowCount(1020)
        table_dock_widget = QtAds.CDockWidget("Table 2")
        table_dock_widget.setWidget(table)
        table_dock_widget.setMinimumSizeHintMode(QtAds.CDockWidget.MinimumSizeHintFromDockWidget)
        table_dock_widget.resize(250, 150)
        table_dock_widget.setMinimumSize(200, 150)
        table_area = self.dock_manager.addDockWidget(QtAds.DockWidgetArea.BottomDockWidgetArea, table_dock_widget, table_area)
        self.menuView.addAction(table_dock_widget.toggleViewAction())

        properties_table = QTableWidget()
        properties_table.setColumnCount(3)
        properties_table.setRowCount(10)
        properties_dock_widget = QtAds.CDockWidget("Properties")
        properties_dock_widget.setWidget(properties_table)
        properties_dock_widget.setMinimumSizeHintMode(QtAds.CDockWidget.MinimumSizeHintFromDockWidget)
        properties_dock_widget.resize(250, 150)
        properties_dock_widget.setMinimumSize(200, 150)
        self.dock_manager.addDockWidget(QtAds.DockWidgetArea.RightDockWidgetArea, properties_dock_widget, central_dock_area)
        self.menuView.addAction(properties_dock_widget.toggleViewAction())
        
        # PyQt에서 툴바에 "Perspective" 관련 기능을 추가하는 예시입니다
        self.create_perspective_ui()
        
    def create_perspective_ui(self):
        # **QAction**은 사용자 인터페이스에서 메뉴 항목이나 툴바 버튼 등을 정의하는 클래스입니다.
        # 여기서 save_perspective_action은 "Create Perspective"라는 텍스트를 가진 액션을 생성하며, 이는 이후 툴바에 추가됩니다.
        save_perspective_action = QAction("Create Perspective", self)
        # 이 줄은 "Create Perspective" 버튼이 클릭되었을 때, save_perspective()라는 메서드를 호출하는 트리거(이벤트)를 연결합니다.
        save_perspective_action.triggered.connect(self.save_perspective)
        # **QWidgetAction**은 일반적인 QAction과는 달리, 위젯을 포함한 액션을 정의할 수 있습니다. 
        # 여기서 perspective_list_action은 위젯(콤보박스)를 포함하는 액션을 정의합니다. 이 액션은 나중에 툴바에 추가됩니다.
        perspective_list_action = QWidgetAction(self)
        # **QComboBox**는 여러 항목을 선택할 수 있는 드롭다운 메뉴를 제공하는 위젯입니다. 
        # perspective_combobox는 도킹 레이아웃을 저장하고 나중에 불러올 수 있도록 저장된 "Perspective" 리스트를 보여주는 콤보박스입니다.
        self.perspective_combobox = QComboBox(self)
        # 이 줄은 콤보박스의 크기 조정 정책을 설정합니다. AdjustToContents는 콤보박스의 크기가 내부에 들어가는 내용에 맞춰서 자동으로 조정된다는 의미입니다.
        self.perspective_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        # 이 줄은 콤보박스의 크기 정책을 설정합니다. 이 설정을 통해 콤보박스가 창의 크기가 조정될 때 어떻게 크기를 변경할지를 결정합니다. Preferred는 가급적 적당한 크기를 유지하라는 의미입니다
        self.perspective_combobox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # 이 줄은 사용자가 콤보박스에서 항목을 선택할 때 발생하는 이벤트를 연결합니다. 사용자가 특정 레이아웃을 선택하면, openPerspective() 메서드가 호출되어 그 레이아웃이 불러와집니다.
        self.perspective_combobox.activated[str].connect(self.dock_manager.openPerspective)
        # perspective_list_action의 기본 위젯을 콤보박스로 설정하는 코드입니다. 이 줄을 통해 콤보박스가 툴바에서 액션으로 동작하게 됩니다.
        perspective_list_action.setDefaultWidget(self.perspective_combobox)
        # 툴바에 구분선을 추가하는 코드입니다. 이는 여러 액션이나 위젯 사이에 구분을 주어 사용자 인터페이스가 더 깔끔하게 보이도록 합니다.
        self.toolBar.addSeparator()
        # 툴바에 콤보박스(저장된 레이아웃 목록)를 추가하는 코드입니다. 이렇게 하면 사용자가 툴바에서 레이아웃을 선택할 수 있게 됩니다.
        self.toolBar.addAction(perspective_list_action)
        # 툴바에 "Create Perspective" 버튼을 추가하는 코드입니다. 사용자가 이 버튼을 클릭하면 현재 도킹 레이아웃을 저장할 수 있습니다.
        self.toolBar.addAction(save_perspective_action)
        
    def save_perspective(self):
        perspective_name, ok = QInputDialog.getText(self, "Save Perspective", "Enter Unique name:")
        if not ok or not perspective_name:
            return
        
        self.dock_manager.addPerspective(perspective_name)
        blocker = QSignalBlocker(self.perspective_combobox)
        self.perspective_combobox.clear()
        self.perspective_combobox.addItems(self.dock_manager.perspectiveNames())
        self.perspective_combobox.setCurrentText(perspective_name)
        
    def closeEvent(self, event: QCloseEvent):
        self.dock_manager.deleteLater()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    w = MainWindow()
    w.show()
    app.exec_()
