from flask import Flask, render_template, request, jsonify
import sqlite3
import random

app = Flask(__name__)


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
        default_items = [("Пицца", 20), ("Кофе", 30), ("Книга", 10), ("Ничего", 40)]
        cursor.executemany("INSERT INTO wheel_items (text, chance) VALUES (?, ?)", default_items)
    conn.commit()
    conn.close()


init_db()


@app.route('/')
def home():
    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT text, chance FROM wheel_items")
    items = [{"text": row[0], "chance": row[1]} for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', items=items)


@app.route('/spin', methods=['POST'])
def spin():
    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT text, chance FROM wheel_items")
    items = [{"text": row[0], "chance": row[1]} for row in cursor.fetchall()]

    total = sum(item["chance"] for item in items)
    rand = random.uniform(0, total)
    current = 0

    for item in items:
        if current + item["chance"] >= rand:
            cursor.execute("INSERT INTO history (item_text) VALUES (?)", (item["text"],))
            conn.commit()
            conn.close()
            return jsonify({"result": item["text"]})
        current += item["chance"]

    conn.close()
    return jsonify({"result": "Ничего"})


@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.json
    text = data.get("text")
    chance = int(data.get("chance", 0))

    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(chance) FROM wheel_items")
    total = cursor.fetchone()[0] or 0

    if total + chance > 100:
        conn.close()
        return jsonify({"status": "error", "message": "Сумма шансов не может превышать 100%"}), 400

    cursor.execute("INSERT INTO wheel_items (text, chance) VALUES (?, ?)", (text, chance))
    conn.commit()
    conn.close()
    return jsonify({"status": "OK"})


@app.route('/remove_item', methods=['POST'])
def remove_item():
    data = request.json
    text = data.get("text")

    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wheel_items WHERE text = ?", (text,))
    conn.commit()
    conn.close()
    return jsonify({"status": "OK"})


@app.route('/get_items')
def get_items():
    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT text, chance FROM wheel_items")
    items = [{"text": row[0], "chance": row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


if __name__ == '__main__':
    app.run(debug=True)