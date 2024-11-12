from .common import *
import copy

class WireframeStrainCalculator():
    marker_matrix = np.array([
        [-1, -1, -1, -1, -1, +1, +1, +1, -1],
        [-1, -1, -1, +1, +1, +1, +1, +1, -1],
        [-1, -1, +1, +1, +1, +1, +1, +1, -1],
        [+1, +1, +1, +1, +1, +1, +1, +1, -1],
        [+1, +1, +1, +1, +1, +1, +1, +1, +1],
        [+1, +1, +1, +1, -1, -1, -1, -1, -1],
        ])
    
    def __init__(self):
        self.indexed_marker_matrix = None

    def get_wireframe_strain(self):
        # df = copy.deepcopy(df_input)
        # 1~34 마커는 순서 변경 없이 사용
        # df.iloc[:, 0:35]

        nrows, ncols = np.shape(self.marker_matrix)
        
        # marker_matrix와 크기가 같고, 모든 요소가 -1인 배열 생성
        self.indexed_marker_matrix = np.full((nrows, ncols), -1)

        # 마커가 존재하는 곳에 마커의 index를 부여한 matrix 생성
        count = 0
        for i in range(ncols):
            for j in range(nrows):
                if self.marker_matrix[j, i] == 1:
                    self.indexed_marker_matrix[j, i] = count
                    count += 1

        print(self.marker_matrix)
        print(self.indexed_marker_matrix)
        
    

# function strain = CalculateStrain(rawData, markerMatrix)
#     data = zeros(size(rawData, 1), 35, 3);
#     % Wireframe 구성용 마커는 순서 변경 없이 사용
#     data(:, (1:34), :) = rawData(:, (1:34), :);
#     % 팔꿈치 마커를 35번으로 변경
#     data(:, 35, :) = rawData(:, 38, :);
    
#     row = size(markerMatrix, 1);
#     col = size(markerMatrix, 2);

#     % 인덱싱
#     count = 1;
#     for i = 1:col
#         for j = 1:row
#             if markerMatrix(j, i) == 1
#                 markerMatrix(j, i) = count;
#                 count = count+1;
#             end
#         end
#     end
    
#     % Horizontal
#     count = 1;
#     for i = 1:col-1
#         for j = 1:row
#             if markerMatrix(j, i) > 0
#                 if markerMatrix(j, i+1) > 0
#                     horiStrain(:, count) = findlength(data, markerMatrix(j, i), markerMatrix(j, i+1)) * 1000 / 50;
#                     count = count+1;
#                 end
#             end
#         end
#     end

#     % Vertical
#     count = 1;
#     for i = 1:col
#         for j = 1:row-1
#             if markerMatrix(j, i) > 0
#                 if markerMatrix(j+1, i) > 0
#                     vertLen(:, count) = findlength(data, markerMatrix(j, i), markerMatrix(j+1, i)) * 1000 / 50;
#                     count = count+1;
#                 end
#             end
#         end
#     end
    
#     % Lower diagonal
#     count = 1;
#     for i = 1:col-1
#         for j = 1:row-1
#             if markerMatrix(j, i) > 0
#                 if markerMatrix(j+1, i+1) > 0
#                     upperDStrain(:, count) = findlength(data, markerMatrix(j, i), markerMatrix(j+1, i+1)) * 1000 / 70;
#                     count = count+1;
#                 end
#             end
#         end
#     end
    
#     % Upper diagonal
#     count = 1;
#     for i = 1:col-1
#         for j = 2:row
#             if markerMatrix(j, i) > 0
#                 if markerMatrix(j-1, i+1) > 0
#                     lowerDStrain(:, count) = findlength(data, markerMatrix(j, i), markerMatrix(j-1, i+1)) * 1000 / 70;
#                     count = count+1;
#                 end
#             end
#         end
#     end
#     strain = [horiStrain, vertLen, upperDStrain, lowerDStrain];
# end

# function dataOut = findlength(markerData, startPoint, endPoint)

#     leng = 0;
#     for i = 1:3
#         leng = leng + (markerData(:, startPoint, i)-markerData(:, endPoint, i)).^2;
#     end
   
#     dataOut(:, 1) = sqrt(leng);
# end

class WireframeStrainCalculationWidget(QWidget):
    def __init__(self, json_data_manager, parent=None):
        self.parent= parent
        super().__init__(self.parent)

        self.calculaotor = WireframeStrainCalculator()

        self.json_data_manager = json_data_manager

        self.__init_ui()

    def __init_ui(self):
        def __set_button_style(button, height):
            button.setFixedSize(0, height)
            button.setMinimumSize(0, height)
            button.setMaximumSize(16777215, height)
            button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            button.setStyleSheet(f"""
                                  QPushButton {{
                                      background-color: {PyQtAddon.get_color("point_color_1")};
                                      color: {PyQtAddon.get_color("content_text_color")};
                                      padding: 4px 8px;
                                      border-radius: 0px;
                                      border: none;
                                  }}
                                  QPushButton:hover {{
                                      background-color: {PyQtAddon.get_color("point_color_5")};
                                      border: none;
                                  }}
                                  """)
            
        # 레이아웃 생성
        layout = QVBoxLayout()
        self.setLayout(layout)
            
        # strain 데이터 계산 버튼
        button = QPushButton("Calculate strain", self.parent)
        button.clicked.connect(self.__calculate_wireframe_strain)
        __set_button_style(button, 20)

        # 레이아웃에 위젯 추가
        layout.addWidget(button)
        
        self.setMaximumHeight(300)
        self.setStyleSheet(f"""
                            QWidget {{
                                margin: 0px;
                                padding: 0px;
                                background-color: {PyQtAddon.get_color("background_color")};
                                }}""")
     
    def __calculate_wireframe_strain(self):
        self.calculaotor.get_wireframe_strain()