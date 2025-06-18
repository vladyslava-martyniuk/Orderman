from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('menu.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/menu")
def menu():
    sort_order = request.args.get("sort", "asc")
    selected_category = request.args.get("category", "all")

    conn = get_db_connection()

    categories = conn.execute("SELECT DISTINCT category FROM dishes").fetchall()


    if selected_category == "all":
        dishes = conn.execute(f"""
            SELECT * FROM dishes
            ORDER BY category ASC, price {'DESC' if sort_order == 'desc' else 'ASC'}
        """).fetchall()
    else:
        dishes = conn.execute(f"""
            SELECT * FROM dishes
            WHERE category = ?
            ORDER BY price {'DESC' if sort_order == 'desc' else 'ASC'}
        """, (selected_category,)).fetchall()

    conn.close()

    return render_template("menu.html", menu=dishes,
                           sort_order=sort_order,
                           categories=categories,
                           selected_category=selected_category)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        category = request.form["category"]

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO dishes (title, description, price, quantity, category)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, price, quantity, category))

        conn.commit()
        conn.close()
        return redirect("/menu")

    return render_template("admin_form.html")

if __name__ == "__main__":
    app.run(debug=True)