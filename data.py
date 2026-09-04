import sqlite3

def createdb():
    con = sqlite3.connect("tasks.db")
    cur = con.cursor()
    return con,cur

def initialize_tasks_table(cur):
    cur.execute("CREATE TABLE tasks(id int PRIMARY KEY, title varchar(255), done BOOL)")
    return

def insert_three_samples(con,cur):
    cur.execute( "INSERT INTO tasks(id, title, done) VAlUES (1,'Task 1',False),(2,'Task 2',TRUE),(3,'Task 3',False)" )
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

if __name__ == "__main__":
    con,cur = createdb()
    if not cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'").fetchone():
        initialize_tasks_table(cur=cur)
    insert_three_samples(con, cur)
    get_all_tasks(cur=cur)
    con.close()