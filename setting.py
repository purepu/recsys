import sqlite3
from memdb import load, save

# SQLite Database File Path
DB_NAME = 'recexpr2.db'

# training table name
RATING_TABLE = 'core_train'

USE_KNN = True
# the number of neighbours in KNN
N_NEIGHBOURS = 37

# should database be loaded into memory at first
USE_MEMDB = False

# Below is auto-generated
if USE_MEMDB:
    conn = load(DB_NAME)
else:
    conn = sqlite3.connect(DB_NAME)

# some meta-data
N_USERS = int(conn.execute('SELECT COUNT(DISTINCT user_id) FROM core_rating').fetchone()[0])
N_MOVIES = int(conn.execute('SELECT COUNT(DISTINCT movie_id) FROM core_rating').fetchone()[0])
