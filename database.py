import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    country TEXT,
    kyc_status TEXT DEFAULT 'pending',
    balance REAL DEFAULT 0,
    referrer INTEGER,
    total_deposit REAL DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    txid TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS profits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    start_date TEXT,
    end_date TEXT,
    status TEXT DEFAULT 'Active'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    wallet TEXT,
    status TEXT
)
""")

conn.commit()
try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN active_contract REAL DEFAULT 0"
    )
    conn.commit()
    print("active_contract column added")
except:
    print("active_contract already exists")