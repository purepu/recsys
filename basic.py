import sqlite3
from setting import *
from math import sqrt

# Each function whose name starts with '_' is an inner function 
# that are not ought to be called outside.

def sim(u, v):
    '''sim(u, v) returns Pearson Correlation Coefficient ranging from -1 to 1 between u and v'''
    # cache layer
    if u > v:
        u, v = v, u
    try:
        return conn.execute('SELECT similarity FROM core_similarity WHERE id = %d' % (u * (N_USERS + 1) + v)).fetchone()[0]
    except TypeError:
        # hit unsuccessful leads to fetchone() returning None
        pass
    # compute similarity between two users
    I = corate(u, v)
    ru = get_adjusted_ratings(u, I)
    rv = get_adjusted_ratings(v, I)
    try:
        # vector cosine computation
        return sum([ru[i] * rv[i] for i in range(0, len(I))]) / sqrt(sum([r ** 2 for r in ru])) / sqrt(sum([r ** 2 for r in rv]))
    except ZeroDivisionError:
        # exception occurs only when ratings of user are all zeros.
        return 0

def corate(u, v):
    '''returns movie_id(ASC) which is co-rated by both u and v'''
    return [e[0] for e in conn.execute('SELECT movie_id FROM %s WHERE user_id = %d AND movie_id IN (SELECT movie_id FROM %s WHERE user_id = %d) ORDER BY movie_id ASC' % (RATING_TABLE, u, RATING_TABLE, v)).fetchall()]

def get_adjusted_ratings(u, I):
    '''returns all ratings(ASC by movie_id and ratings are adjusted by baseline function) rated by u to items in I, which are not allowed to be None'''
    ratings = get_ratings(u, I)
    base = baseline(u, I)
    return [r - base for r in ratings]

def get_ratings(u, I):
    '''returns raw ratings(ASC by movie_id) rated by u to items in I, which are not allowed to be None'''
    return [r[1] for r in conn.execute('SELECT movie_id, rating FROM %s WHERE user_id = %d AND movie_id IN %s ORDER BY movie_id ASC' % (RATING_TABLE, u, _genstr(I))).fetchall()]

def baseline(u, I=None):
    '''used to adjust raw ratings using proper way, i.e. average rating of a given user'''
    if I:
        group = _genstr(I)
        return conn.execute('SELECT AVG(rating) FROM %s WHERE user_id = %d AND movie_id IN %s' % (RATING_TABLE, u, group)).fetchone()[0]
    return conn.execute('SELECT AVG(rating) FROM %s WHERE user_id = %d' % (RATING_TABLE, u)).fetchone()[0]

def _genstr(lst):
    '''lst  [1, 2, 3]
    return  '(1, 2, 3)'
    '''
    buf = ['(']
    buf.append(str(lst)[1:-1])
    buf.append(')')
    return ''.join(buf)

def guess(user, movie):
    '''traditional guessing method using average baseline'''
    neighbours = conn.execute('SELECT user_id, rating FROM %s WHERE user_id != %d AND movie_id = %d ORDER BY user_id ASC' % (RATING_TABLE, user, movie)).fetchall()
    if not neighbours:
        return baseline(user)
    simlist = [(sim(user, u[0]), u[0], u[1] - baseline(u[0])) for u in neighbours] # [sim_value, user_id, score - preference]
    cmp = lambda x, y: 1 if abs(x[0]) > abs(y[0]) else (0 if abs(x[0]) == abs(y[0]) else -1)
    simlist.sort(cmp, reverse = True)
    if USE_KNN:
        N = min(len(simlist), N_NEIGHBOURS)
    else:
        N = len(simlist)
    _sum = 0
    _sum_sim = 0
    for i in range(0, N):
        _sum += simlist[i][0] * simlist[i][2]
        _sum_sim += abs(simlist[i][0])
    _sum /= _sum_sim
    return _sum + baseline(user)

def cache(init=False):
    '''making the cache layer of similarity'''
    if init:
        conn.execute('DELETE FROM core_similarity')
    for i in range(1, N_USERS + 1):
        for j in range(i, N_USERS + 1):
            try:
                conn.execute('INSERT INTO core_similarity VALUES(%d, %f)' % (i * (N_USERS + 1) + j, sim(i, j)))
                print i, j
            except sqlite3.IntegrityError:
                pass
        conn.commit()

def mae(guess=guess, *args):
    '''calculate the MAE value using guess function'''
    rs = conn.execute('SELECT user_id, movie_id, rating FROM core_test ORDER BY user_id, movie_id ASC').fetchall()
    _mae = 0
    i = 0
    N = len(rs)
    for r in rs:
        _mae += abs(guess(r[0], r[1], *args) - r[2])
        i += 1
        if not i % 100:
            print i, N
    return _mae * 1.0 / len(rs)

if __name__ == '__main__':
    print 'loading finished!'
    print mae()
