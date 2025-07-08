from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)

# === Налаштування погоди ===
API_KEY  = "8e92e4ce26e06d4f3c425901fbf9847b" 
LAT = 60.2055
LON = 24.6559

# === БД ===
def get_db_connection():
    conn = sqlite3.connect("menu.db")
    conn.row_factory = sqlite3.Row
    return conn

# === Отримати прогноз погоди ===
def get_weather():
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"lat={LAT}&lon={LON}&appid={API_KEY}&units=metric&lang=ua"
        )
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            return "Не вдалося отримати прогноз погоди."
        
        city = data.get("name", "невідомо")
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"Погода в {city}: {temp}°C, {desc}"
    except Exception as e:
        return f"Помилка при отриманні погоди: {e}"

# === Маршрути ===
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/weather")
def weather_page():
    weather = get_weather()
    return render_template("weather.html", weather=weather)

@app.route("/menu")
def menu():
    sort_order = request.args.get("sort", "asc")
    conn = get_db_connection()
    order_by = "DESC" if sort_order == "desc" else "ASC"
    dishes = conn.execute(f"SELECT * FROM dishes ORDER BY price {order_by}").fetchall()
    conn.close()
    return render_template("menu.html", menu=dishes, sort_order=sort_order, search=None)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "").strip()
        quantity = request.form.get("quantity", "").strip()
        category = request.form.get("category", "").strip()

        if not title or not price or not category:
            return "Назва, ціна та категорія обов'язкові.", 400

        try:
            price_val = float(price)
        except ValueError:
            return "Ціна має бути числом.", 400

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO dishes (title, description, price, quantity, category)
            VALUES (?, ?, ?, ?, ?)
        """,
            (title, description, price_val, quantity, category),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("menu"))

    return render_template("admin_form.html", book=None, mode="add")

@app.route("/edit/<int:dish_id>", methods=["GET", "POST"])
def edit(dish_id):
    conn = get_db_connection()
    dish = conn.execute("SELECT * FROM dishes WHERE id = ?", (dish_id,)).fetchone()
    if dish is None:
        conn.close()
        return "Страва не знайдена", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "").strip()
        quantity = request.form.get("quantity", "").strip()
        category = request.form.get("category", "").strip()

        if not title or not price or not category:
            return "Назва, ціна та категорія обов'язкові.", 400

        try:
            price_val = float(price)
        except ValueError:
            return "Ціна має бути числом.", 400

        conn.execute(
            """
            UPDATE dishes SET title = ?, description = ?, price = ?, quantity = ?, category = ?
            WHERE id = ?
        """,
            (title, description, price_val, quantity, category, dish_id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("menu"))

    conn.close()
    return render_template("admin_form.html", book=dish, mode="edit")

@app.route("/delete/<int:dish_id>", methods=["POST"])
def delete(dish_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("menu"))

@app.route("/search")
def search():
    search_query = request.args.get("q", "").strip().lower()
    conn = get_db_connection()
    dishes = conn.execute("SELECT * FROM dishes").fetchall()
    conn.close()
    filtered = [dish for dish in dishes if search_query in dish["title"].lower()]
    return render_template("menu.html", menu=filtered, search=search_query)

@app.route("/clear-menu", methods=["POST"])
def clear_menu():
    conn = get_db_connection()
    conn.execute("DELETE FROM dishes")
    conn.commit()
    conn.close()
    return redirect(url_for("menu"))

if __name__ == "__main__":
    app.run(debug=True)
