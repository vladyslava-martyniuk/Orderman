import sqlite3

def clear_dishes_table():
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dishes")  # очищення записів
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='dishes'")  # скидання автоінкремента id
    conn.commit()
    conn.close()
    print("Таблиця dishes успішно очищена.")

def init_db():
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()

    # Створити таблицю, якщо її немає
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
    ''')

    cursor.execute("PRAGMA table_info(dishes)")
    columns = [info[1] for info in cursor.fetchall()]

    if 'quantity' not in columns:
        cursor.execute("ALTER TABLE dishes ADD COLUMN quantity TEXT")
    if 'category' not in columns:
        cursor.execute("ALTER TABLE dishes ADD COLUMN category TEXT")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
