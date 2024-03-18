import numpy as np

# Z 배열 예시 생성
Z = np.random.choice([0, 1], size=20, p=[0.7, 0.3])

# 1인 인덱스와 0인 인덱스 찾기
indices_of_1 = np.where(Z == 1)[0]
indices_of_0 = np.where(Z == 0)[0]

# 각각에서 랜덤하게 하나씩 인덱스 선택
index_to_turn_0 = np.random.choice(indices_of_1, 1)[0]
index_to_turn_1 = np.random.choice(indices_of_0, 1)[0]

# 선택된 인덱스의 값을 변경
Z[index_to_turn_0] = 0
Z[index_to_turn_1] = 1

print(Z)
