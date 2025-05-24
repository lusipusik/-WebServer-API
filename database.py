import sqlite3

def init_db():
    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wheel_items (
        id INTEGER PRIMARY KEY,
        text TEXT NOT NULL,
        chance INTEGER NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        item_text TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    if cursor.execute("SELECT COUNT(*) FROM wheel_items").fetchone()[0] == 0:
        default_items = [("Перекус", 20), ("Настолка", 30), ("Почитать книги", 10), ("Поспать", 40)]
        cursor.executemany("INSERT INTO wheel_items (text, chance) VALUES (?, ?)", default_items)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()