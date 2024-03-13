import numpy as np
import random
from util.util import Adj_matrix_demand_generate
import time 
import cplex
from scipy.sparse import csr_matrix, save_npz

nnode=[100,150,200]

for n in nnode:
    adj=np.load("data/adj{}_4000.npz".format(n))
    adj0 = adj['arr_0']
    newadj=adj0[ : , : int(0.8*n), int(-0.2*n) :]
    
    asdf=0
    np.savez_compressed('data/newadj{}_4000.npz'.format(n), newadj)