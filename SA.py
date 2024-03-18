import numpy as np
import random
from util.util import Adj_matrix_demand_generate
import time 
import math
import cplex
from scipy.sparse import csr_matrix, save_npz

def Swap(Z):
    indices_of_1 = np.where(Z == 1)[0]
    indices_of_0 = np.where(Z == 0)[0]

    # 각각에서 랜덤하게 하나씩 인덱스 선택
    index_to_turn_0 = np.random.choice(indices_of_1, 1)[0]
    index_to_turn_1 = np.random.choice(indices_of_0, 1)[0]

    # 선택된 인덱스의 값을 변경
    Z[index_to_turn_0] = 0
    Z[index_to_turn_1] = 1
    
    return Z


def Followers_problem(Z_current,adj, demand, parameter):
    p=parameter['p']
    r=parameter['r']
    
    Neighbor = [[] for _ in range(n-p)]

    
    for j in range(n-p):
        num_neighbor=0
        for i in range(p):
            if adj[j][i] ==1:
                Neighbor[j].append(i)
                
        
    problem=cplex.Cplex()
    problem.objective.set_sense(problem.objective.sense.minimize)
    u=["u{}".format(j) for j in range(n-p)]
    s=["s{}".format(i) for i in range(p)]
    for j in range(n-p):
        problem.variables.add(names=[u[j]],lb=[0],ub=[1],types=['B'], obj=[demand[j]])
    for i in range(p):
        problem.variables.add(names=[s[i]],lb=[0],ub=[1],types=['B'])
        
    #제약식 (6)
    var, coef= [],[]
    for i in range(p):
        var.append(s[i])
        coef.extend([1])
    problem.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                senses = "E", rhs=[r])
    #제약식 (7)
    for j in range(n-p):
        if len(Neighbor[j]) !=0:
            for i in Neighbor[j]:
                var=[u[j],s[i]]
                coef=[1,1]
                problem.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                        senses = "G", rhs=[1])
        
        
        else:
            var=[u[j]]
            coef=[1]
            problem.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                        senses = "E", rhs=[0])
    #제약식(8)
    for i in range(p):
        rhs=round(1-Z_current[i])
        var=[s[i]]
        coef=[1]
        problem.linear_constraints.add(lin_expr=[cplex.SparsePair(var,coef)], \
                        senses = "L", rhs=[rhs])
    
    problem.solve()
    problem.write("testSA.lp")
    f_new=problem.solution.get_objective_value()
    
    return f_new
    
nset=[150,200,300]
ndata=10


for n in nset:
    adj=np.load("data/Test_adj{}_10.npz".format(n))['arr_0']
    demand=np.load("data/Test_demand{}_10.npz".format(n))['arr_0']
    result=open("result/SAresult{}.txt".format(n),"w")
    for data_index in range(ndata):
        start_time=time.perf_counter()
        T0=100
        Tf=1
        delta=0.99
                
        parameter={"p":int(0.2*n), "q":int(0.05*n), "r":int(0.05*n) }  
        p=parameter['p']
       
        adj_slice=adj[:, :n-p, n-p:]
        
        
        (_,n_customer )=demand.shape
        n_facility=n-n_customer
        
        Z_init=np.zeros(n_facility)
        # 랜덤 위치 선택
        random_indices = np.random.choice(n_facility, parameter['r'], replace=False)
        # 선택된 위치의 값을 1로 변경
        Z_init[random_indices] = 1
        f_best=Followers_problem(Z_init, adj_slice[data_index],demand[data_index],parameter)
        T=T0
        Z_best=Z_init
        
        Z_current=Z_init
        f_current=f_best
        while T> Tf:
            Z_prime=Swap(Z_current)
            f_prime=Followers_problem(Z_current, adj_slice[data_index],demand[data_index],parameter)
            E=f_current-f_prime
            if E<0:
                Z_current=Z_prime
                f_current=f_prime
            else:
                low= np.random.rand()
                if low > math.exp(-abs(E)/T): 
                    Z_current=Z_prime
                    f_current=f_prime
            
            if f_current>f_best:
                f_best=f_current
                Z_best=Z_current
            T=T*delta
        end_time=time.perf_counter()
        result.write("{}        {}      {}\n".format(data_index, f_best, end_time-start_time))
    result.close()
            
   
   
    