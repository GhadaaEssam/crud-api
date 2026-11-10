import sqlite3

def createdb():
    """
    Create a connection to the SQLite database and return the connection and cursor.
    Returns:
        con: sqlite3.Connection - The connection object to the SQLite database.
        cur: sqlite3.Cursor - The cursor object to execute SQL commands.
    """
    con = sqlite3.connect("tasks.db")
    cur = con.cursor()
    return con,cur

def get_db_connection():
    """
    Context manager to provide a database connection and cursor.
    Yields:
        con: sqlite3.Connection - The connection object to the SQLite database.
        cur: sqlite3.Cursor - The cursor object to execute SQL commands.
    """
    con, cur = createdb()
    try:
        yield con, cur
    finally:
        con.close()

def initialize_database():
    """
    Initialize the database by creating the tasks table if it doesn't exist.
    """
    con, cur = createdb()
    try:
        initialize_tasks_table(cur)
        con.commit()
    finally:
        con.close()

def initialize_tasks_table(cur):
    """
    Create the tasks table in the database if it doesn't exist.
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check if the created_at and updated_at columns exist, and add them if they don't
    cur.execute("PRAGMA table_info(tasks)")
    columns = {row[1] for row in cur.fetchall()}

    if "created_at" not in columns:
        cur.execute("ALTER TABLE tasks ADD COLUMN created_at TEXT")
    if "updated_at" not in columns:
        cur.execute("ALTER TABLE tasks ADD COLUMN updated_at TEXT")

    # Update existing rows to have the current timestamp for created_at and updated_at
    cur.execute("UPDATE tasks SET created_at=CURRENT_TIMESTAMP WHERE created_at IS NULL")
    cur.execute("UPDATE tasks SET updated_at=CURRENT_TIMESTAMP WHERE updated_at IS NULL")

def insert_three_samples(con,cur):
    """
    Insert three sample tasks into the database.
    """
    cur.execute( """
        INSERT INTO tasks(title, done) 
        VAlUES ('Task 1',False),('Task 2',TRUE),('Task 3',False)
    """ )
    con.commit()
    print("done")

def get_all_tasks(cur):
    """
    Get all tasks from the database.
    Returns a list of all tasks.
    """
    cur.execute( "Select * FROM tasks")
    tasks = cur.fetchall()
    return tasks

def get_task_by_id(cur, id):
    """
    Get a task by its ID.
    Returns the task if found, otherwise returns None.
    """
    cur.execute( "Select * FROM tasks WHERE id=?", (id,))
    task = cur.fetchone()
    return task

def insert_task(con, cur, title,done=False):
    """
    Insert a new task into the database.
    Returns the ID of the newly created task.
    """
    cur.execute("INSERT INTO tasks(title, done, created_at, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", (title, done))
    con.commit()
    return cur.lastrowid

def alter_task(con, cur, id, title=None, done=None):
    """
    Update a task's title and/or done status by its ID.
    If title is None, it won't be updated.
    If done is None, it won't be updated.
    """
    if title is not None and done is not None:
        cur.execute("UPDATE tasks SET title=?, done=? , updated_at=CURRENT_TIMESTAMP WHERE id=?", (title, done, id))
    elif title is not None:
        cur.execute("UPDATE tasks SET title=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (title, id))
    elif done is not None:
        cur.execute("UPDATE tasks SET done=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (done, id))
    con.commit()

    return get_task_by_id(cur, id)

def remove_task(con, cur, id):
    """
    Remove a task by its ID.
    Returns True if the task was removed, False if the task was not found.
    """
    cur.execute("DELETE FROM tasks WHERE id=?", (id,))
    if cur.rowcount == 0:
        return False
    con.commit()
    return True

def get_filtered_tasks(cur,name=None ,done=None):
    """
    Get tasks filtered by name and/or done status.
    If name is provided, it will filter tasks that contain the name in their title.
    If done is provided, it will filter tasks based on their done status (True or False
    """
    Query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if name is not None:
        Query += " AND title LIKE ?"
        params.append(f"%{name}%")

    if done is not None:
        Query += " AND done = ?"
        params.append(done)

    Query += " ORDER BY title ASC"

    cur.execute(Query, params) 
    return cur.fetchall()

def get_statistics(cur):
    """
    Get statistics about the tasks in the database.
    Returns a dictionary containing the total number of tasks, 
    the number of completed tasks, and the number of pending tasks.
    """
    cur.execute("""
        SELECT
            COUNT(*) AS total,
            COUNT(CASE WHEN done=1 THEN 1 END) AS completed,
            COUNT(CASE WHEN done=0 THEN 1 END) AS pending,
            COALESCE(
                ROUND(100.0 * COUNT(CASE WHEN done=1 THEN 1 END) / NULLIF(COUNT(*), 0), 2),
                0
            ) AS done_percentage
        FROM tasks;
    """)
    stats = cur.fetchone()
    total_tasks = stats[0]
    completed_tasks = stats[1]
    pending_tasks = stats[2]
    done_percentage = stats[3]

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "done_percentage":done_percentage
    }

if __name__ == "__main__":
    con,cur = createdb()
    if not cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'").fetchone():
        initialize_tasks_table(cur=cur)
    get_all_tasks(cur=cur)
    con.close()