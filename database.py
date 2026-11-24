import sqlite3
import os

# For EXE: Database lives in C:\GomaRestro\ so it survives updates
BASE_DIR = os.path.join(os.path.expanduser("~"), "GomaRestro")
os.makedirs(BASE_DIR, exist_ok=True)
DB_PATH = os.path.join(BASE_DIR, "goma_restro.db")
BACKUP_DIR = os.path.join(BASE_DIR, "Backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Settings Table - Business Info
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        business_name TEXT DEFAULT 'GomaRestro Demo',
        phone TEXT DEFAULT '0770 000 000',
        location TEXT DEFAULT 'Kampala, Uganda',
        tin TEXT DEFAULT '',
        receipt_footer TEXT DEFAULT 'Thank you, come again!',
        vat_percent REAL DEFAULT 0,
        service_charge REAL DEFAULT 0
    )
    """)

    # Tables Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        capacity INTEGER DEFAULT 4,
        status TEXT DEFAULT 'Free'
    )
    """)

    # Menu Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        cost REAL DEFAULT 0,
        available INTEGER DEFAULT 1
    )
    """)

    # Users Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        pin TEXT UNIQUE
    )
    """)

    # Activity Log
    cur.execute("""
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        action TEXT,
        date_time TEXT
    )
    """)

    # Default Settings
    cur.execute("SELECT COUNT(*) FROM settings")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO settings (business_name) VALUES ('GomaRestro Demo')")

    # Default Tables
    cur.execute("SELECT COUNT(*) FROM tables")
    if cur.fetchone()[0] == 0:
        defaults = [("Table 1",4),("Table 2",4),("Table 3",6),("VIP 1",8),("Garden 1",6),("Bar Counter",4)]
        cur.executemany("INSERT INTO tables (name, capacity) VALUES (?,?)", defaults)

    # Default Menu
    cur.execute("SELECT COUNT(*) FROM menu")
    if cur.fetchone()[0] == 0:
        items = [
            ("Grilled Chicken","Food",25000,12000),
            ("Rolex","Food",8000,4000),
            ("Pilau","Food",15000,7000),
            ("Nile Beer","Drinks",8000,5000),
            ("Soda","Drinks",5000,3000),
            ("Cocktail","Cocktails",15000,7000),
        ]
        cur.executemany("INSERT INTO menu (name,category,price,cost) VALUES (?,?,?,?)", items)

    # Default Users - Admin 1234, Waiter 1111
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO users (name,role,pin) VALUES (?,?,?)", [
            ("Admin","Admin","1234"),
            ("John Waiter","Waiter","1111"),
            ("Mary Cashier","Cashier","2222"),
        ])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database created at:", DB_PATH)
