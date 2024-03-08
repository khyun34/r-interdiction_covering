import numpy as np
from scipy.sparse import csr_matrix, save_npz

data=np.load("data/adj.npz")
print(data.files)
print(data['arr_0'])
print(data['arr_0'][0])
# 특정 배열에 접근하기
# 예를 들어, 'arr_0'이라는 이름의 배열에 접근하려면 다음과 같이 합니다.


# 사용 후 .npz 파일 객체 닫기
data.close()