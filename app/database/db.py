import sqlite3

def createdb():
    con = sqlite3.connect("tasks.db")
    cur = con.cursor()
    return con,cur

def get_db_connection():
    con, cur = createdb()
    try:
        yield con, cur
    finally:
        con.close()

def initialize_database():
    con, cur = createdb()
    try:
        initialize_tasks_table(cur)
        con.commit()
    finally:
        con.close()

def initialize_tasks_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0, 1))
        )
    """)
    return

def insert_three_samples(con,cur):
    cur.execute( """
        INSERT INTO tasks(title, done) 
        VAlUES ('Task 1',False),('Task 2',TRUE),('Task 3',False)
    """ )
    con.commit()
    print("done")

def get_all_tasks(cur):
    cur.execute( "Select * FROM tasks")
    tasks = cur.fetchall()
    return tasks

def get_task_by_id(cur, id):
    cur.execute( "Select * FROM tasks WHERE id=?", (id,))
    task = cur.fetchone()
    return task

def insert_task(con, cur, title,done=False):
    cur.execute("INSERT INTO tasks(title, done) VALUES (?, ?)", (title, done))
    con.commit()
    return cur.lastrowid

def alter_task(con, cur, id, title=None, done=None):
    if title is not None and done is not None:
        cur.execute("UPDATE tasks SET title=?, done=? WHERE id=?", (title, done, id))
    elif title is not None:
        cur.execute("UPDATE tasks SET title=? WHERE id=?", (title, id))
    elif done is not None:
        cur.execute("UPDATE tasks SET done=? WHERE id=?", (done, id))
    con.commit()

    return get_task_by_id(cur, id)

def remove_task(con, cur, id):
    cur.execute("DELETE FROM tasks WHERE id=?", (id,))
    if cur.rowcount == 0:
        return False
    con.commit()
    return True

if __name__ == "__main__":
    con,cur = createdb()
    if not cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'").fetchone():
        initialize_tasks_table(cur=cur)
    insert_three_samples(con, cur)
    get_all_tasks(cur=cur)
    con.close()