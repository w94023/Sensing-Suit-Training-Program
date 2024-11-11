from .common import *

class AdjustableGridLayout(QWidget):
    def __init__(self, minimum_grid_width=25, minimum_grid_height=25, parent=None):
        super().__init__(parent)
        
        # flags
        self.__apply_minimum_size_clamping = True

        # 키워드를 격자 형태로 배치하기 위해 GridLayout 생성
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
    
        # 레이아웃 설정
        self.setLayout(self.grid_layout)

        # grid 최소 width 및 height 저장
        self.minimum_grid_width = minimum_grid_width
        self.minimum_grid_height = minimum_grid_height

        # 표시할 grid item 저장
        self.__grid_items = []
        
        # ngrid를 기반으로 계산된 row, col 수
        self.__nrows = 0
        self.__ncols = 0
        
        # 과도한 업데이트 방지
        self.__is_updating = False
        
    def enable_minimum_size_clamping(self, enable):
        """계산된 행,열로 도출된 최소 창 크기를 size policy에 적용시킬 지 여부를 결정하는 메서드. Default to True

        Args:
            enable (bool): True > clamping 적용, False > clamping 미적용
        """
        
        self.__apply_minimum_size_clamping = enable
        self.__apply_widget_minimum_size()
        
    def set_items(self, items):
        """Grid에 표시될 layout 혹은 widget 설정하는 메서드"""
        self.__grid_items = items
        self.__set_layout()
        
    def get_layout(self):
        """Grid layout 반환하는 메서드

        Returns:
            QGridLayout: grid_layout
        """
        return self.grid_layout
    
    def get_grid_size(self):
        """Grid layout의 사이즈 반환하는 메서드

        Returns:
            int: nrows
            int: ncols
        """
        return self.__nrows, self.__ncols
    
    def resizeEvent(self, event):
        """윈도우 크기가 변경될 때 호출"""
        self.__update_layout()
        super().resizeEvent(event)
        
    def __get_rows_cols(self):
        """창의 폭을 기준으로 grid 행, 열의 개수 계산"""
        widget_width = self.width()
        ngrid = len(self.__grid_items)
        
        # 최대 열 계산
        self.__ncols = min(max(1, widget_width // self.minimum_grid_width), ngrid)
        
        # 행 계산
        self.__nrows = math.ceil(ngrid / self.__ncols)
        
        # 행과 열을 고르게 분산시키기 위해 열 다시 계산
        # [ngrid:7 > nrows:2, ncols:6] >> [ngrid:7 > nrows:2, ncols:4]
        self.__ncols = math.ceil(ngrid / self.__nrows)
        
    def __apply_widget_minimum_size(self):
        """창의 최소 크기 계산 후 업데이트"""
        
        if not self.__apply_minimum_size_clamping:
            self.setMinimumSize(0, 0)
            return
        
        else:
            # 창의 최소 크기 계산
            minimum_widget_width = self.__ncols *  self.minimum_grid_width
            minimum_widget_height = self.__nrows *  self.minimum_grid_height
            
            # 창의 최소 크기 업데이트
            self.setMinimumSize(minimum_widget_width, minimum_widget_height)
        
    def __set_layout(self):
        """주어진 grid item에 따라 grid의 행,열을 계산하고 grid에 요소 배치하는 메서드"""
        if self.__is_updating:
            return
        
        if len(self.__grid_items) == 0:
            return
        
        self.__is_updating = True
        
        # grid 초기화
        delete_widgets(self.grid_layout)

        # 창의 폭을 기준으로 열의 개수 계산
        self.__get_rows_cols()
        
        # 창의 최소 크기 계산
        self.__apply_widget_minimum_size()
        
        # grid 요소 배치
        count = 0
        for i in range(self.__nrows):
            for j in range(self.__ncols):
                if isinstance(self.__grid_items[count], QWidget):
                    self.grid_layout.addWidget(self.__grid_items[count], i, j)
                elif isinstance(self.__grid_items[count], QLayout):
                    self.grid_layout.addLayout(self.__grid_items[count], i, j)
                count += 1
                
                if count == len(self.__grid_items):
                    break
                
        self.__is_updating = False
        
    def __update_layout(self):
        """재계산된 grid의 행,열에 따라 grid 요소 재배치하는 메서드"""
        
        if self.__is_updating:
            return
        
        if len(self.__grid_items) == 0:
            return
        
        self.__is_updating = True
        
        # 창의 폭을 기준으로 열의 개수 계산
        self.__get_rows_cols()
        
        # 창의 최소 크기 계산
        self.__apply_widget_minimum_size()

        # grid 요소 재배치
        count = 0
        for i in range(self.__nrows):
            for j in range(self.__ncols):
                self.__change_widget_index(self.__grid_items[count], i, j)
                count += 1
                
                if count == len(self.__grid_items):
                    break
                
        self.__is_updating = False
            
    def __change_widget_index(self, widget, new_row, new_column):
        """지정된 위젯을 새로운 행과 열 위치로 이동"""
        # Widget일 때,
        if isinstance(widget, QWidget):
            
            # 현재 위젯을 grid_layout에서 제거
            for i in range(self.grid_layout.count()):
                item = self.grid_layout.itemAt(i)
                if item and item.widget() == widget:
                    self.grid_layout.removeWidget(widget)
                    break
                
            # 새로운 위치에 widget 추가
            self.grid_layout.addWidget(widget, new_row, new_column)
            
        # Layout일 때,
        elif isinstance(widget, QLayout):
            
            # 현재 layout을 grid_layout에서 제거
            for i in range(self.grid_layout.count()):
                item = self.grid_layout.itemAt(i)
                if item and item.layout() == widget:
                    self.grid_layout.removeItem(widget)
                    break
                
            # 새로운 위치에 layout 추가
            self.grid_layout.addLayout(widget, new_row, new_column)
        
    def clear(self):
        """Layout 및 인스턴스 데이터 비우기"""
        self.__grid_items.clear()
        self.__nrows = 0
        self.__ncols = 0
        
        delete_widgets(self.grid_layout)
        self.__update_layout()