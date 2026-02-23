import sqlite3

DB_NAME = "timelogs.db"

def conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    c = conn().cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        date TEXT,
        team TEXT,
        project TEXT,
        sub_activity TEXT,
        category TEXT,
        start_time TEXT,
        end_time TEXT,
        duration REAL,
        comments TEXT
    )
    """)

    # Default admin
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users(username,password,role) VALUES ('admin','admin123','Admin')")

    conn().commit()

def add_user(u,p,r):
    conn().execute("INSERT INTO users(username,password,role) VALUES (?,?,?)",(u,p,r))
    conn().commit()

def get_users():
    return conn().execute("SELECT username,role FROM users").fetchall()

def validate_user(u,p):
    return conn().execute("SELECT role FROM users WHERE username=? AND password=?",(u,p)).fetchone()

def insert_log(data):
    conn().execute("""
    INSERT INTO logs(username,date,team,project,sub_activity,category,start_time,end_time,duration,comments)
    VALUES (?,?,?,?,?,?,?,?,?,?)
    """, data)
    conn().commit()

def get_logs():
    return conn().execute("SELECT * FROM logs").fetchall()
