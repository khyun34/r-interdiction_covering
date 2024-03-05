import numpy as np

lst = [10, 20, 5, 40]

# 내림차순으로 정렬된 요소의 인덱스를 구함
indices_desc = sorted(range(len(lst)), key=lambda x: lst[x], reverse=True)

print(indices_desc)
