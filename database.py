import sqlite3


def init_db():
    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()

    # Таблица элементов колеса
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wheel_items (
        id INTEGER PRIMARY KEY,
        text TEXT NOT NULL,
        chance INTEGER NOT NULL
    )
    ''')

    # Таблица истории выигрышей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        item_text TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Начальные данные (если таблица пуста)
    if cursor.execute("SELECT COUNT(*) FROM wheel_items").fetchone()[0] == 0:
        default_items = [
            ("Пицца", 20),
            ("Кофе", 30),
            ("Книга", 10),
            ("Ничего", 40)
        ]
        cursor.executemany("INSERT INTO wheel_items (text, chance) VALUES (?, ?)", default_items)

    conn.commit()
    conn.close()


init_db()