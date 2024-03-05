import numpy as np
from util.util import Adj_matrix_demand_generate
import time 
import cplex

#수치 정의
ratio=2
global n,p,q,r
global Neighbor,demand
n=int(100*ratio)
p=int(20*ratio)
# q=1
# r=2
# q=int(2.5*ratio)
r=int(2.5*ratio)
# criterion=0.081
criterion=0.15

show_plt=True

#lognormal 분포 파라미터

mu=2.845565678551321
sigma_squared=1.4759065198095778

start_time=time.perf_counter()

#adj_mat   1,2,3,... n-p :customer n-p+1,....,n:facility, faciliyt들의 인덱스는 0,1,2,...,p-1 
#demand : p-dimention numpy array, Neighbor:n-p dimension list, 각 list트는 인접한 facility들의 인덱스들의집합
adj_mat, demand, Neighbor, max_C=Adj_matrix_demand_generate(n,p,criterion,mu,sigma_squared,show_plt)

ip_obj=np.zeros(p+1)
lp_obj=np.zeros(p+1)


start_time=time.perf_counter()
for k in range(p+1):
    ip=cplex.Cplex()
    ip.objective.set_sense(ip.objective.sense.minimize)
    
    s,u =[],[]
    
    s=["s{}".format(i) for i in range(p)]
    u=["u{}".format(j) for j in range(n-p)]
    
    for i in range(p):
        ip.variables.add(names=[s[i]],lb=[0],ub=[1],types=["B"])
    for j in range(n-p):
        ip.variables.add(names=[u[j]],lb=[0],ub=[1],types=["B"], obj=[demand[j]])
        
    x_bar=np.zeros(p)
    
    if k!=p:
        x_bar[k]=1
        
    #제약식(6)
    var=["s{}".format(i) for i in range(p)]
    coef=[1]*p
    ip.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                    senses = "E", rhs=[r]) 
    
    #제약식(7)
    for j in range(n-p):
        if len(Neighbor[j]) !=0:
            for _ ,facility_index  in enumerate(Neighbor[j]):
                var=[u[j],s[facility_index]]
                coef=[1,1]
                ip.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                                senses = "G", rhs=[1])
        else:
            var=["u{}".format(j)]
            coef=[1]
            ip.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                                senses = "E", rhs=[0])
    #제약식(8)
    for i in range(p):
        var=["s{}".format(i)]
        coef=[1]
        ip.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                                senses = "L", rhs=[1-x_bar[i]])
    
    ip.solve()
    
    
    ip_obj[k]=ip.solution.get_objective_value()


ip_time=time.perf_counter() -start_time



lp_sort=np.argsort(lp_obj)[::-1]
ip_sort=np.argsort(lp_obj)[::-1]

print("p={}".format(p))
print(lp_sort)
print(ip_sort)
print(lp_obj)
print(ip_obj)


print("lp_time={} ".format(lp_time))
print("ip_time={} ".format(ip_time))
safsdf=0
        
            
    

