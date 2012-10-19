import unittest
from random import random
from setting import *
from svd import *

class TestSVD(unittest.TestCase):
    def setUp(self):
        self.matrix = listize()

    def test_listize(self):
        for entry in conn.execute('SELECT user_id, movie_id, rating FROM core_train').fetchall():
            self.assertEqual(self.matrix[entry[0] - 1][entry[1] - 1], entry[2])

    def test_fill(self):
        fill(self.matrix)
        pos = []
        for i in range(0, N_USERS):
            for j in range(0, N_MOVIES):
                if self.matrix[i][j] == 0:
                    pos.append((i, j))
        avgs = dict(conn.execute('SELECT movie_id, AVG(rating) FROM core_train GROUP BY movie_id').fetchall())
        for p in pos:
            self.assertEqual(self.filled_matrix[p[0]][p[1]], avgs.get(p[1] + 1, 3))

    def test_normalize(self):
        fill(self.matrix)
        normalize(self.matrix)
        avgs = dict(conn.execute('SELECT user_id, AVG(rating) FROM core_train GROUP BY user_id').fetchall())
        for entry in conn.execute('SELECT user_id, movie_id, rating FROM core_train').fetchall():
            self.assertEqual(self.matrix[entry[0] - 1][entry[1] - 1], entry[2] - avgs[entry[0]])

    def test_mysvd(self):
        pass

if __name__ == '__main__':
    unittest.main()
