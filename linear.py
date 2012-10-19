import sqlite3
from setting import *
from basic import sim, get_ratings, baseline, mae, corate
from scipy.optimize import fmin
from numpy import array

def guess(user, movie):
    '''experimental guessing method using linear transformational function'''
    neighbours = conn.execute('SELECT user_id, rating FROM %s WHERE user_id != %d AND movie_id = %d ORDER BY user_id ASC' % (RATING_TABLE, user, movie)).fetchall()
    if not neighbours:
        return baseline(user)
    simlist = [(sim(user, u[0]), u[0], u[1]) for u in neighbours] # [abs(sim_value), user_id, score]
    # return sum([gen_func(e[1], user)(e[2]) for e in simlist]) * 1.0 / len(simlist)
    cmp = lambda x, y: 1 if abs(x[0]) > abs(y[0]) else (0 if abs(x[0]) == abs(y[0]) else -1)
    simlist.sort(cmp, reverse = True)
    if USE_KNN:
        N = min(len(simlist), N_NEIGHBOURS)
    else:
        N = len(simlist)
    _sum = 0
    _sum_sim = 0
    for i in range(0, N):
        _sum += abs(simlist[i][0]) * gen_func(simlist[i][1], user)(simlist[i][2])
        _sum_sim += abs(simlist[i][0])
    _sum /= _sum_sim
    return _sum

def gen_func(u, v):
    '''R(v) = a + b * R(u)'''
    # cache layer
    try:
        a, b = conn.execute('SELECT a, b FROM core_func WHERE id = %d' % (u * (N_USERS + 1) + v)).fetchone() 
        return lambda x: a + b * x
    except:
        pass
    # unsuccessful hit
    I = corate(u, v)
    ru = get_ratings(u, I)
    rv = get_ratings(v, I)
    return _gen_func(ru, rv)

def _gen_func(ru, rv):
    '''[rv] = a + b * [ru]'''
    ru, rv = array(ru), array(rv)
    fp = lambda x, p: p[0] + p[1] * x
    e = lambda p, y, x: abs(fp(x, p) - y).sum()
    p = fmin(e, array([0, 1]), args = (rv, ru), maxiter = 10000, maxfun = 10000, disp = 0)
    return lambda x: fp(x, p)

def cache(init = False):
    '''caching function parameters -- a and b in R(v) = a + b * R(u)'''
    if init:
        conn.execute('DELETE FROM core_func')
    x = conn.execute('SELECT MAX(id) FROM core_func').fetchone()[0] / (N_USERS + 1)
    for i in range(x + 1, N_USERS + 1):
        for j in range(1, N_USERS + 1):
            try:
                I = corate(i, j)
                ru, rv = array(get_ratings(i, I)), array(get_ratings(j, I))
                fp = lambda x, p: p[0] + p[1] * x
                e = lambda p, y, x: abs(fp(x, p) - y).sum()
                p = fmin(e, array([0, 1]), args = (rv, ru), maxiter = 10000, maxfun = 10000, disp = 0)
                a, b = p[0], p[1]
                conn.execute('INSERT INTO core_func VALUES(%d, %lf, %lf)' % (i * (N_USERS + 1) + j, a, b))
            except sqlite3.IntegrityError:
                print 'chongfu!'
        print i
        conn.commit()

def draw():
    from pylab import figure, xlabel, ylabel, plot, legend, grid, show
    X = range(1, 23, 2)
    Yt = [1.084, 0.878, 0.826, 0.803, 0.790, 0.782, 0.776, 0.772, 0.768, 0.765, 0.763]
    Yn = [1.094, 0.879, 0.822, 0.783, 0.770, 0.762, 0.757, 0.754, 0.753, 0.752, 0.750]
    figure(0)
    xlabel('K')
    ylabel('MAE')
    p1, = plot(X, Yt, 'b^-')
    p2, = plot(X, Yn, 'rs-')
    legend([p1, p2], ['normal', 'linear'])
    grid(True)
    show()

if __name__ == '__main__':
    draw()
