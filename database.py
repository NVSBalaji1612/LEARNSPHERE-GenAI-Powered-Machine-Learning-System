import sqlite3

def create_connection():
    conn = sqlite3.connect("learnsphere.db")
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Performance table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        topic TEXT,
        level TEXT,
        score INTEGER,
        total_questions INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()