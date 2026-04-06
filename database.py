"""
database.py - Data persistence module.

Manage the connection with the SQLite database and the structure initialization
of the tables from Production Order System.

Author: João Vitor Kasteller Debeterco
Date: 2026
Version 1.0.0
SENAI Jaragua do Sul - Tecnico em Cibersistemas para Automacao WEG
"""

import sqlite3

BASE_NAME = "orders.db"
"""str: Path to the SQlite database file."""

def get_connection():
    """
    Create and return a connection with the database SQLite.

    The property row_factory allow access by the columns names
    (ex: order['product']) instead of index (ex: order[1]).

    Return:
    sqlite3.Connection: connection object to the database.

    Example:
        >>> conn = get_connection()
        >>> cursor = conn.cursor()
        >>> cursor.execute('SELECT 1')
        >>> conn.close()
    """
    conn = sqlite3.connect(BASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize the database creating the table 'orders' 
    if dont exist. Secure to call multiple times.

    The table contains the fields:
        id         - auto-increment primary key
        product    - product name (required)
        quantity   - pieces quantity (required)
        status     - order status (default: Pending)
        created_at - timestamp of creation (automatic)

    Returns:
        None

    Side effects:
        Create orders.db file if dont exist.
        Print confirmation message in the console.
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