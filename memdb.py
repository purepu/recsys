def load(path):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    fileconn = sqlite3.connect(path)
    for s in fileconn.iterdump():
        try:
            conn.execute(s)
        except:
            pass
    fileconn.close()
    return conn

def save(conn, path):
    import os
    try:
        os.remove(path)
    except OSError:
        pass
    import sqlite3
    target = sqlite3.connect(path)
    for s in conn.iterdump():
        try:
            target.execute(s)
        except:
            pass
    target.commit()
    target.close()
