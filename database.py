import sqlite3
from datetime import datetime

DB_PATH = "estimates.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            project_type TEXT NOT NULL,
            sq_meters REAL NOT NULL,
            budget REAL NOT NULL,
            total_cost REAL NOT NULL,
            took_loan INTEGER NOT NULL,
            surplus REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_estimate(project_type, sq_meters, budget, total_cost, took_loan, surplus):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO estimates (timestamp, project_type, sq_meters, budget, total_cost, took_loan, surplus)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), project_type, sq_meters, budget, total_cost, int(took_loan), surplus))
    
    # DELETE must be INSIDE this function, after INSERT
    cursor.execute("DELETE FROM estimates WHERE id NOT IN (SELECT id FROM estimates ORDER BY id DESC LIMIT 5)")
    
    conn.commit()
    conn.close()

def get_recent_estimates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estimates ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return rows

init_db()