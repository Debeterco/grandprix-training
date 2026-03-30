import sqlite3

BASE_NAME = "orders.db"
def get_connection():
    """
    Create and return a connection with the database SQLite.
    The property row_factory allow access by the columns names
    (ex: ordem['produto']) instead of index (ex: ordem[1]).
    Return:
    sqlite3.Connection: connection object to the database.
    """
    conn = sqlite3.connect(BASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize the database creating the table 'orders' 
    if dont exist. Secure to call multiple times.
    """
conn = get_connection()
cursor = conn.cursor() # cursor() allow execute SQL commands
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT DEFAULT 'Pendent',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
)
''')

conn.commit()   # commit() save alterations in the orders.db
conn.close()    # close() free the connection (good practice)
print("Database initialization succeeded.")