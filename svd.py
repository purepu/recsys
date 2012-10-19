# svd.py is to implement dimentional reduction of rating matrix

from setting import *
from scipy import linalg, dot
from numpy import array
from basic import mae
from numpy import sqrt, sum, abs

# Caching some often-used data
USER_AVERAGE = dict(conn.execute('SELECT user_id, AVG(rating) FROM core_train GROUP BY user_id').fetchall())
MOVIE_AVERAGE = dict(conn.execute('SELECT movie_id, AVG(rating) FROM core_train GROUP BY movie_id').fetchall())
SIM_TABLE = dict(conn.execute('SELECT id, similarity FROM core_similarity ORDER BY id').fetchall())

def listize():
    '''convert table core_train, which consists of entries, into a rating 2D-list.'''
    m = []
    for i in range(0, N_USERS):
        m.append([])
        existed = dict(conn.execute('SELECT movie_id, rating FROM core_train WHERE user_id = %d ORDER BY movie_id ASC' % (i+1)).fetchall())
        for j in range(0, N_MOVIES):
            m[i].append(existed.get(j + 1, 0))
    return m

def fill(m):
    '''fill empty area with average ratings of movie'''
    for i in range(0, N_USERS):
        for j in range(0, N_MOVIES):
            if m[i][j] == 0:
                m[i][j] = MOVIE_AVERAGE.get(j + 1, 3)

def normalize(m):
    '''substract raw ratings with user's average rating'''
    for i in range(0, N_USERS):
        for j in range(0, N_MOVIES):
            m[i][j] -= USER_AVERAGE.get(i + 1, 3)

def approximation(m, k = 1):
    '''Do singular value decomposition according to k, which will lower rank to k * rank'''
    U, s, Vh = linalg.svd(m, False)
    tarlen = int(k * len(s))
    s = s[:tarlen]
    U = U.T[:tarlen].T
    V = Vh[:tarlen].T
    return dot(U, dot(linalg.diagsvd(s, len(s), len(s)), V.T))

def init(k = 1):
    '''called before guess'''
    m = listize()
    fill(m)
    normalize(m)
    return approximation(m, k)

def guess(user, movie, M):
    '''Brilliant guess function'''
    return USER_AVERAGE.get(user, 3) + M[user - 1][movie - 1]

def sim(u, v, M, SIM_TABLE = None):
    if SIM_TABLE:
        if u > v:
            u, v = v, u
        return SIM_TABLE[u * (N_USERS + 1) + v]
    return sum(M[u-1] * M[v-1]) * 1.0 / sqrt(sum(M[u-1] ** 2) * sum(M[v-1] ** 2))

def guess2(user, movie, M):
    '''traditional guessing method using average baseline'''
    neighbours = range(1, N_USERS + 1)
    simlist = [(sim(user, u, M, SIM_TABLE), M[u-1][movie-1]) for u in neighbours] # [sim_value, score - preference]
    cmp = lambda x, y: 1 if abs(x[0]) > abs(y[0]) else (0 if abs(x[0]) == abs(y[0]) else -1)
    simlist.sort(cmp, reverse = True)
    if USE_KNN:
        simlist = simlist[:N_NEIGHBOURS]
    A = array([e[0] for e in simlist])
    B = array([e[1] for e in simlist])
    return sum(A * B) * 1.0 / sum(abs(A)) + USER_AVERAGE[user]

def draw():
    from pylab import figure, xlabel, ylabel, plot, legend, grid, show
    from numpy import arange
    X = [0.29499999999999998, 0.28999999999999998, 0.28499999999999998, 0.28000000000000003, 0.27500000000000002, 0.27000000000000002, 0.26500000000000001, 0.26000000000000001, 0.255, 0.25, 0.245, 0.23999999999999999, 0.23499999999999999, 0.23000000000000001, 0.22500000000000001, 0.22, 0.215, 0.20999999999999999, 0.20499999999999999, 0.20000000000000001, 0.19500000000000001, 0.19, 0.185, 0.17999999999999999, 0.17499999999999999, 0.17000000000000001, 0.16500000000000001, 0.16, 0.155, 0.14999999999999999, 0.14499999999999999, 0.14000000000000001, 0.13500000000000001, 0.13, 0.125, 0.12, 0.115, 0.11, 0.105, 0.10000000000000001, 0.095000000000000001, 0.089999999999999997, 0.085000000000000006, 0.080000000000000002, 0.074999999999999997, 0.070000000000000007, 0.065000000000000002, 0.059999999999999998, 0.055, 0.050000000000000003, 0.044999999999999998, 0.040000000000000001, 0.035000000000000003, 0.029999999999999999, 0.025000000000000001, 0.02, 0.014999999999999999, 0.01, 0.0050000000000000001, -0.0]
    Y = [0.80954199999999998, 0.80937999999999999, 0.80906199999999995, 0.80900099999999997, 0.80885700000000005, 0.80832400000000004, 0.80835299999999999, 0.80793599999999999, 0.80774900000000005, 0.80765299999999995, 0.80738299999999996, 0.80729600000000001, 0.80649099999999996, 0.80632199999999998, 0.80612399999999995, 0.80572600000000005, 0.80510899999999996, 0.80458799999999997, 0.80404900000000001, 0.80375799999999997, 0.80301599999999995, 0.80234399999999995, 0.80177900000000002, 0.80118400000000001, 0.80075600000000002, 0.80046700000000004, 0.799987, 0.79962699999999998, 0.79881500000000005, 0.79875799999999997, 0.79854599999999998, 0.79780300000000004, 0.79726200000000003, 0.79710999999999999, 0.796435, 0.79627700000000001, 0.79619200000000001, 0.79458200000000001, 0.79408699999999999, 0.79299600000000003, 0.79289799999999999, 0.79177299999999995, 0.79007700000000003, 0.78931700000000005, 0.78781000000000001, 0.78671500000000005, 0.78576999999999997, 0.78374900000000003, 0.78226600000000002, 0.78073099999999995, 0.779335, 0.77730200000000005, 0.77637699999999998, 0.77458700000000003, 0.77288100000000004, 0.77128699999999994, 0.77002300000000001, 0.76909400000000006, 0.770034, 0.78199600000000002]
    figure(0)
    xlabel('K')
    ylabel('MAE')
    p1, = plot(X, Y, 'b-', linewidth = 2)
    grid(True)
    show()

if __name__ == '__main__':
    from time import time
    M = init(0.01)
    t = time()
    print mae(guess, M)
    print time() - t
