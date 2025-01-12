from .common import *
import copy

class Calculator():
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
        
    def __get_strain(self, df, index1, index2, initial_length):
        # 데이터가 들어갈 빈 행렬 생성
        len = np.zeros((df.shape[0], 1))
        
        # X, Y, Z축 차이의 제곱 더하기
        # .to_numpy() 적용 시, (nrow, ) 형식으로 나오기 때문에, (nrow, 1) 형식으로 np.reshape 필요
        len += ((df.iloc[:, 3*index1+0 + 1].to_numpy() - df.iloc[:, 3*index2+0 + 1].to_numpy()) ** 2).reshape(np.shape(len)[0], 1) # X축
        len += ((df.iloc[:, 3*index1+1 + 1].to_numpy() - df.iloc[:, 3*index2+1 + 1].to_numpy()) ** 2).reshape(np.shape(len)[0], 1) # Y축
        len += ((df.iloc[:, 3*index1+2 + 1].to_numpy() - df.iloc[:, 3*index2+2 + 1].to_numpy()) ** 2).reshape(np.shape(len)[0], 1) # Z축

        # sqrt 적용
        len = np.sqrt(len)
        
        # strain 게산 (%단위)
        strain = (len-initial_length)/initial_length * 100

        return strain
        
    def get_wireframe_strain(self, df):
        # df = copy.deepcopy(df_input)
        # 1~34 마커는 순서 변경 없이 사용
        # df.iloc[:, 0:35]

        nrows, ncols = np.shape(self.marker_matrix)
        
        # marker_matrix와 크기가 같고, 모든 요소가 -1인 배열 생성
        self.indexed_marker_matrix = np.full((nrows, ncols), -1)

        # 마커가 존재하는 곳에 마커의 index를 부여한 matrix 생성
        count = 0
        for i in range(ncols):
            for j in range(nrows-1, -1, -1): # 루프 역순으로 돌리기 (5, 4, 3, 2, 1, 0)
                if self.marker_matrix[j, i] == 1:
                    self.indexed_marker_matrix[j, i] = count
                    count += 1

        wireframe_strain = []
        # horizontal wireframe
        for i in range(ncols-1):
            for j in range(nrows-1, -1, -1):
                if self.indexed_marker_matrix[j, i] > -1:
                    if self.indexed_marker_matrix[j, i+1] > -1:
                        wireframe_strain.append(self.__get_strain(df, self.indexed_marker_matrix[j ,i], self.indexed_marker_matrix[j, i+1], 50))
                            
        # vertical wireframe
        for i in range(ncols):
            for j in range((nrows-1)-1, -1, -1):
                if self.indexed_marker_matrix[j, i] > -1:
                    if self.indexed_marker_matrix[j+1, i] > -1:
                        wireframe_strain.append(self.__get_strain(df, self.indexed_marker_matrix[j ,i], self.indexed_marker_matrix[j+1, i], 50))
                            
        # lower diagonal wireframe
        for i in range(ncols-1):
            for j in range((nrows-1)-1, -1, -1):
                if self.indexed_marker_matrix[j, i] > -1:
                    if self.indexed_marker_matrix[j+1, i+1] > -1:
                        wireframe_strain.append(self.__get_strain(df, self.indexed_marker_matrix[j ,i], self.indexed_marker_matrix[j+1, i+1], 70))
                            
        # upper diagonal wireframe
        for i in range(ncols-1):
            for j in range(nrows-1, 0, -1):
                if self.indexed_marker_matrix[j, i] > -1:
                    if self.indexed_marker_matrix[j-1, i+1] > -1:
                        wireframe_strain.append(self.__get_strain(df, self.indexed_marker_matrix[j ,i], self.indexed_marker_matrix[j-1, i+1], 70))
                            
        # 리스트의 배열을 가로로 병합하여 변환
        wireframe_strain_array = np.hstack(wireframe_strain)
        
        # column 생성
        df_columns = []
        for i in range(len(wireframe_strain)):
            df_columns.append("Wireframe"+str(i+1))
        
        # DataFrame으로 변환
        df_wireframe = pd.DataFrame(wireframe_strain_array, columns=df_columns)
        
        # Time 행 삽입
        df_combined = pd.concat([df.iloc[:, [0]], df_wireframe], axis=1)
        
        return df_combined