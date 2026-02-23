import sqlite3

DB_NAME = "timelogs.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():

    with get_connection() as conn:
        c = conn.cursor()

        # Users table
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
        """)

        # Logs table
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

        # Ensure admin exists
        c.execute("SELECT * FROM users WHERE username=?", ("admin",))
        if not c.fetchone():
            c.execute(
                "INSERT INTO users (username,password,role) VALUES (?,?,?)",
                ("admin","admin123","Admin")
            )

        conn.commit()


def add_user(username, password, role):

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO users(username,password,role) VALUES (?,?,?)",
            (username,password,role)
        )
        conn.commit()


def get_users():

    with get_connection() as conn:
        return conn.execute("SELECT username, role FROM users").fetchall()


def validate_user(username, password):

    with get_connection() as conn:
        return conn.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username,password)
        ).fetchone()


def insert_log(data):

    with get_connection() as conn:
        conn.execute("""
        INSERT INTO logs(username,date,team,project,sub_activity,category,start_time,end_time,duration,comments)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """, data)
        conn.commit()


def get_logs():

    with get_connection() as conn:
        return conn.execute("SELECT * FROM logs").fetchall()
