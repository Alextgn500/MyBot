import sqlite3
import os


def create_tables():
    """Создает необходимые таблицы в базе данных"""
    connection = sqlite3.connect("my_database.db")
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER
    ) 
    ''')

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON Users(email)")

    # Создаем таблицу продуктов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image_path TEXT
    )
    ''')

    connection.commit()
    connection.close()
    print("Таблицы успешно созданы")


def add_test_products():
    """Добавляет тестовые продукты в базу данных"""
    connection = sqlite3.connect("my_database.db")
    cursor = connection.cursor()

    # Проверяем, есть ли данные в таблице Products
    cursor.execute('SELECT COUNT(*) FROM Products')
    count = cursor.fetchone()[0]

    # Если данных нет, добавляем тестовые продукты
    if count == 0:
        print("Добавляем тестовые продукты в базу данных...")

        # Тестовые продукты
        products_data = [
            (1, 'Продукт 1', 'Натуральный комплекс для ускорения метаболизма', 400.0, 'files/product1.jpg'),
            (2, 'Продукт 2', 'Пищевые волокна для контроля аппетита', 600.0, 'files/product2.jpg'),
            (3, 'Продукт 3', 'Витаминный комплекс с L-карнитином', 800.0, 'files/product3.jpg'),
            (4, 'Продукт 4', 'Протеиновый коктейль для снижения веса', 1000.0, 'files/product4.jpg'),
            (5, 'Продукт 5', 'Морской коллаген с комплексом витаминов', 1200.0, 'files/product5.jpg')
        ]

        # Вставляем данные
        cursor.executemany('INSERT INTO Products VALUES (?, ?, ?, ?, ?)', products_data)
        connection.commit()
        print(f"Добавлено {len(products_data)} тестовых продуктов")
    elif count > 0:
        print(f"В базе данных уже есть {count} продуктов. Пропускаем добавление тестовых данных.")

    connection.close()


def check_database():
    """Проверяет состояние базы данных"""
    db_path = 'my_database.db'
    if os.path.exists(db_path):
        print(f"База данных {db_path} существует")

        # Проверяем таблицы
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Таблицы в базе данных: {[table[0] for table in tables]}")

        # Проверяем наличие данных в Products
        if any(table[0] == 'Products' for table in tables):
            cursor.execute("SELECT COUNT(*) FROM Products")
            count = cursor.fetchone()[0]
            print(f"Количество записей в таблице Products: {count}")

            if count > 0:
                cursor.execute("SELECT id, title, price FROM Products LIMIT 3")
                sample = cursor.fetchall()
                print(f"Примеры продуктов: {sample}")

        conn.close()
    else:
        print(f"База данных {db_path} не существует")


def init_db():
    """Инициализирует базу данных: создает таблицы и добавляет тестовые данные"""
    create_tables()
    add_test_products()
    check_database()


# Если файл запущен напрямую, инициализируем базу данных
if __name__ == "__main__":
    init_db()

