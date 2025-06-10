from flask import Flask, render_template, request

app = Flask(__name__)

menu_items = [
    {"title": "Маргарита", "description": "Томатний соус, моцарела, базилік", "price": 120},
    {"title": "Пепероні", "description": "Моцарела, пепероні, томатний соус", "price": 140},
    {"title": "Гавайська", "description": "Шинка, ананас, моцарела, соус", "price": 135},
    {"title": "Кальцоні", "description": "Томатний соус, моцарела, соус", "price": 120}
]
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/menu")
def menu():
    sort_order = request.args.get("sort", "asc")
    sorted_menu = sorted(
        menu_items, key=lambda x: x["price"], reverse=(sort_order == "desc")
    )
    return render_template("menu.html", menu=sorted_menu, sort_order=sort_order)


if __name__ == "__main__":
    app.run(debug=True)

