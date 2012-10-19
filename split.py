#! /usr/local/bin/python

from setting import conn
from random import random

train = range(1, 100001)
test = []
while len(test) < 20000:
    test.append(train.pop(int(random() * len(train))))

conn.execute('DELETE FROM core_train')
conn.execute('DELETE FROM core_test')
conn.execute('INSERT INTO core_test SELECT * FROM core_rating WHERE id IN %s' % str(tuple(test)))
conn.execute('INSERT INTO core_train SELECT * FROM core_rating WHERE id IN %s' % str(tuple(train)))
conn.commit()
