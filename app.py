from flask import Flask, render_template, request, jsonify
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def home():
    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT text, chance FROM wheel_items")
    items = [{"text": row[0], "chance": row[1]} for row in cursor.fetchall()]
    conn.close()
    return render_template("index.html", items=items)


@app.route("/spin", methods=["POST"])
def spin():
    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()

    # Получаем элементы колеса
    cursor.execute("SELECT text, chance FROM wheel_items")
    items = [{"text": row[0], "chance": row[1]} for row in cursor.fetchall()]

    # Выбираем случайный элемент с учётом шансов
    total = sum(item["chance"] for item in items)
    rand = random.uniform(0, total)
    current = 0
    result = "Ничего"
    for item in items:
        if current + item["chance"] >= rand:
            result = item["text"]
            # Сохраняем в историю
            cursor.execute("INSERT INTO history (item_text) VALUES (?)", (result,))
            conn.commit()
            break
        current += item["chance"]

    conn.close()
    return jsonify({"result": result})


@app.route("/add_item", methods=["POST"])
def add_item():
    data = request.json
    text = data["text"]
    chance = int(data["chance"])

    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()

    # Проверяем сумму шансов
    cursor.execute("SELECT SUM(chance) FROM wheel_items")
    total_chance = cursor.fetchone()[0] or 0

    if total_chance + chance > 100:
        conn.close()
        return jsonify({"status": "error", "message": "Сумма шансов превышает 100%"}), 400

    cursor.execute("INSERT INTO wheel_items (text, chance) VALUES (?, ?)", (text, chance))
    conn.commit()
    conn.close()
    return jsonify({"status": "OK"})


@app.route("/remove_item", methods=["POST"])
def remove_item():
    text = request.json["text"]
    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wheel_items WHERE text = ?", (text,))
    conn.commit()
    conn.close()
    return jsonify({"status": "OK"})


@app.route("/history")
def get_history():
    conn = sqlite3.connect('wheel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT item_text, timestamp FROM history ORDER BY timestamp DESC LIMIT 10")
    history = [{"text": row[0], "time": row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(history)


if __name__ == "__main__":
    app.run(debug=True)