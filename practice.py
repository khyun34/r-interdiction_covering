import cplex
from cplex.callbacks import LazyConstraintCallback

class MyLazyConstraintCallback(LazyConstraintCallback):
    

   
    
    def __call__(self):
        # 현재 해에서 x1과 x2의 값을 가져옵니다.
        x1_value = self.get_values(0)
        x2_value = self.get_values(1)
        x3_value = self.get_values(2)
        
        # x1 + x2 > n 인 경우, 새로운 제약 조건을 추가합니다.
       
            # 이 조건은 x1 + x2 <= n을 의미합니다.
        self.add(constraint=[["x1", "x3"], [1.0,  1.0]], sense="L", rhs=n)

# 사용자가 원하는 n의 값 설정
global n
n = float(2)  # 예시로, n을 1로 설정합니다.

# CPLEX 모델 초기화
prob = cplex.Cplex()

# 목적 함수 방향 설정 (최대화)
prob.objective.set_sense(prob.objective.sense.maximize)

# 변수 추가 (이름: x1, x2, x3)
var_names = ["x1", "x2", "x3"]
prob.variables.add(names=var_names, types=[prob.variables.type.binary] * 3)

# 목적 함수의 계수 설정
obj_coeffs = [1, 2, 3]
prob.objective.set_linear(list(zip(var_names, obj_coeffs)))

# 기본 제약 조건 추가 (x1 + x2 + x3 <= 2)
prob.linear_constraints.add(
    lin_expr=[[var_names, [1.0, 1.0, 1.0]]],
    senses=["L"],
    rhs=[2]
)

# 콜백 등록 (n 값을 콜백 생성자에 전달)
# my_callback = MyLazyConstraintCallback(prob)
# my_callback.set_n(1)  # 예시로 n=1 설정

# 여기에서 콜백을 등록합니다.
prob.register_callback(MyLazyConstraintCallback)
# 문제 해결
prob.solve()

# 결과 출력
print("Solution status =", prob.solution.get_status(), ":", end=' ')
print(prob.solution.status[prob.solution.get_status()])
print("Solution value  =", prob.solution.get_objective_value())
print("Values          = ", prob.solution.get_values())