import sqlite3
from texts14 import PRODUCTS
from texts14 import USERS

# Используем одно имя базы данных везде
DATABASE_NAME = 'my_database.db'

def initiate_db():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        price INT NOT NULL,
        image_path TEXT NOT NULL
    );
    ''')

    cursor.executemany(
        'INSERT INTO Products (title, description, price, image_path) VALUES (?, ?, ?, ?)',
        [(title, desc, price, img) for _, title, desc, price, img in PRODUCTS]
    )

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INT NOT NULL,
        balance INT DEFAULT 1000
    );
    ''')

    cursor.executemany(
        'INSERT INTO Users (username, email, age) VALUES (?, ?, ?)',
        [(username, email, age) for _, username, email, age in USERS]
    )

    connection.commit()
    connection.close()


def get_all_products():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()

    connection.close()
    return products


def add_user(username: str, email: str, age: int):
    try:
        with sqlite3.connect(DATABASE_NAME) as connection:
            cursor = connection.cursor()

            # Добавляем пользователя
            cursor.execute(
                'INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, 1000)',
                (username, email, age)
            )

            # Добавляем commit внутри try блока
            connection.commit()

            # Для проверки добавлен вывод последнего ID
            last_id = cursor.lastrowid
            print(f"Пользователь успешно добавлен с ID: {last_id}")
            return True

    except sqlite3.Error as e:
        print(f"Ошибка при добавлении пользователя: {e}")
        return False


# Для проверки добавлена функция
def get_all_users():
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Users')
        return cursor.fetchall()


def is_included(username):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute('SELECT COUNT(*) FROM Users WHERE username = ?', (username,))
    result = cursor.fetchone()[0] > 0

    connection.close()
    return result


if __name__ == "__main__":
    initiate_db()
    print("База данных создана!")

