import cplex
from cplex.callbacks import LazyConstraintCallback
import numpy as np
import time
import math
import matplotlib.pyplot as plt

class Subproblem(LazyConstraintCallback):
    
    def __call__(self):
        # 현재 솔루션 값 가져오기
        
        y_bar = [round(value) for value in self.get_values(y)]
        z_bar=self.get_values(z)
    
        
        # 부분 문제(Subproblem) 정의 및 해결
        # 예시를 위해 여기서는 간단한 부분 문제를 정의합니다.
        # 실제로는 이 부분에 문제에 맞는 부분 문제를 정의하고 해결하는 코드가 필요합니다.
        # 부분 문제 해결 결과에 따라 위반된 컷을 찾음
        coef, sum_wt, is_violated = self.solve_subproblem(y_bar,z_bar)

        # 위반된 컷이 있는 경우, 주 문제에 컷 추가
        #24.03.01 rhs계산 후 violated cut 추가하는 곳 부터 시작.
        if is_violated==True:
            var=["y{}".format(j) for j in range(n-p)]
            var.extend(["z"])
            self.add(constraint= [var,coef], sense="L", rhs=sum_wt)

    def solve_subproblem(self, y_bar, z_bar):
        sub=cplex.Cplex()
        sub.objective.set_sense(sub.objective.sense.minimize)
       
        t=[ "t{}".format(j) for j in range(n-p)]
        s=[ "s{}".format(i) for i in range(p)]
        
        for j in range(n-p):
            sub.variables.add(names=[t[j]],lb=[0],ub=[1],types=["B"],obj=[demand[j]*(1-y_bar[j])])
        for i in range(p):
            sub.variables.add(names=[s[i]],lb=[0],ub=[1],types=["B"])
        
        #제약식 (17)
        var, coef=[], []
        for i in range(p):
            var.append(s[i])
            coef.extend([1])
        sub.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                    senses = "E", rhs=[r]) 
        
        #제약식 (18)
        
        for j in range(n-p):
            if len(Neighbor[j]) !=0:
                for _, facility_index in enumerate(Neighbor[j]):
                    var,coef=[],[]
                    var.extend([s[facility_index],t[j]])
                    coef.extend([1])
                    coef.extend([1])
                    sub.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                                senses = "G", rhs=[1])
            else: 
                var=["t{}".format(j)]
                coef=[1]
                sub.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                                senses = "E", rhs=[0])
        sub.solve()
        sub_obj=sub.solution.get_objective_value()
        t_bar = [round(value) for value in sub.solution.get_values(t)]
       

        for j in range(n-p):
            sub_obj+=demand[j]*y_bar[j]
        
        # 임시로 위반된 컷을 체크하는 간단한 조건을 설정
        if z_bar > sub_obj:  
            
            coef=[demand[j]*(t_bar[j]-1) for j in range(n-p)]
            coef.extend([1])
            sum_wt=0
            for j in range(n-p):
                sum_wt+= demand[j]*round(t_bar[j])
            is_violoated=True
            return coef, sum_wt, is_violoated
        else:
            is_violoated=False
            return 0, 0, is_violoated  # 위반된 컷이 없는 경우

def plot_points_and_edges(points,p, adjacency_matrix):
    plt.figure(figsize=(8, 6))
    n = len(points)
    # Plot points
    for i in range(n):
        if i<n-p:
            plt.scatter(points[i, 0], points[i, 1], c='green')
            plt.text(points[i][0], points[i][1], f' {demand[i]}', color='red') # demand 값 표시
        else:
            plt.scatter(points[i, 0], points[i, 1], c='blue')
            
        
     
    
    # Plot edges
    
    for i in range(n):
        for j in range(i+1, n):  # Avoid duplicating edges
            if adjacency_matrix[i, j] == 1:  # There's an edge between i and j
                plt.plot([points[i, 0], points[j, 0]], [points[i, 1], points[j, 1]], 'r-')
    
    plt.title('Nodes and Edges')
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.grid(True)
    plt.show()



#수치 정의
ratio=6
global n,p,q,r
global Neighbor,demand
n=int(100*ratio)
p=int(20*ratio)
# q=1
# r=0

q=int(2.5*ratio)
r=int(2.5*ratio)
criterion=0.081
# criterion=0.05

#lognormal 분포 파라미터

mu=2.845565678551321
sigma_squared=1.4759065198095778

start_time=time.perf_counter()

#adjaceny matrix 및 demand 생성 
points = np.round(np.random.rand(n, 2), 4)

adj_mat=np.zeros((n,n))

index=0
for i in range(n-p):
    for j in range(n-p,n):
        distance= math.sqrt((points[i][0]-points[j][0])**2+(points[i][1]-points[j][1])**2)
        
        if distance<=criterion:
            index+=1
            adj_mat[i][j]=1
            adj_mat[j][i]=1

# print(adj_mat)
#adj_mat 형식    1,2...  n-p: custoemr   n-p+1,,,,,,n: facility


demand=np.zeros(n-p)
for i in range(n-p):
    # Generate a random number from a log-normal distribution
    random_number =  np.random.lognormal(mean=mu, sigma=np.sqrt(sigma_squared))

    # Round the number to the nearest integer
    rounded_number = int(round(random_number))
    if rounded_number<1:
        demand[i]=1
    else:
        demand[i]=rounded_number
# print(demand)
# plot_points_and_edges(points,p, adj_mat)
max_C=np.sum(demand)


Neighbor = [[] for _ in range(n-p)]

non_cover_customer=0
for j in range(n-p):
    num_neighbor=0
    for i in range(p):
        if adj_mat[j][n-p+i] ==1:
            Neighbor[j].append(i)
            num_neighbor+=1
    if num_neighbor==0:
        non_cover_customer+=1

print(Neighbor)
        
master=cplex.Cplex()
master.parameters.timelimit.set(600)
master.objective.set_sense(master.objective.sense.maximize)


#x_i: i facility를 보호하면1 아니면 0
#y_j  :N(j)에 속한 facility가 있으면 1 아니면 0
x,y,z=[],[],[]
for j in range(n-p):
    varname= "y"+str(j)
    y.append(varname)
for i in range(n-p,n):
    varname= "x"+str(i-(n-p))
    x.append(varname)
z.append("z")

for j in range(n-p):
    master.variables.add(names=[y[j]],lb=[0],ub=[1],types=['B'])
for i in range(n-p,n):
    master.variables.add(names=[x[i-(n-p)]],lb=[0],ub=[1],types=['B'])
master.variables.add(names=[z[0]],obj=[1],types=['C'])
    

# 제약식 (11)
var,coef=[],[]
for i in range(p):
    var.append(x[i])
    coef.extend([1])
master.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                    senses = "E", rhs=[q])
    
# 제약식 (12)

for j in range(n-p):
    if len(Neighbor[j]) !=0:
        var,coef=[],[]
        var.append(y[j])
        coef.extend([1])
        for _, facility_index in enumerate(Neighbor[j]):
            var.append(x[facility_index])
            coef.extend([-1])
        master.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                        senses = "L", rhs=[0])
    else:
        var=["y"+str(j)]
        coef=[1]
        master.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                        senses = "E", rhs=[0])
    
        
# 제약식 (13)

for j in range(n-p):
    if len(Neighbor[j]) !=0:
        for _, facility_index in enumerate(Neighbor[j]):
            var,coef=[],[]
            var.extend([x[facility_index],y[j]])
            coef.extend([1])
            coef.extend([-1])
            master.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                        senses = "L", rhs=[0])
#제약식 z
var, coef = [],[]
var.append("z")
coef.append(1)
master.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                    senses = "L", rhs=[max_C])


master.register_callback(Subproblem)


master.solve()

#결과출력

print("demand의 합은= {}".format(np.sum(demand)))
print("Solution status =", master.solution.get_status(), ":", end=' ')
print(master.solution.status[master.solution.get_status()])
print("Solution value  =", round(master.solution.get_objective_value()))
print("x_Values          = ", master.solution.get_values(x))
print("y_Values          = ", master.solution.get_values(y))
print("z_Values          = ", master.solution.get_values(z))
print("running time= {}".format(time.perf_counter()-start_time))
print("아무 곳에도 연결되지 않은 커스토머의 비율은={}".format(non_cover_customer/n*1.25))




        