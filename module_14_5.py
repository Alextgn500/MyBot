import os
import sqlite3
import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import FSInputFile
from aiogram.filters import Command
import logging

# Ваши локальные импорты
import texts14
from crud_functions import is_included, add_user, initiate_db
import crud_functions
from db import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_database_tables():
    """Проверяет и создает необходимые таблицы в базе данных"""
    connection = sqlite3.connect('my_database.db')  # Используйте одну базу данных
    cursor = connection.cursor()

    # Проверяем и создаем таблицу Products
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Products'")
    if not cursor.fetchone():
        print("Создаем таблицу Products...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price INT NOT NULL,
            image_path TEXT NOT NULL
        );
        ''')
        print("Таблица Products успешно создана")
    else:
        print("Таблица Products уже существует")

    # Проверяем и создаем таблицу Users
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'")
    if not cursor.fetchone():
        print("Создаем таблицу Users...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            age INT NOT NULL,
            balance INT DEFAULT 1000
        );
        ''')
        print("Таблица Users успешно создана")
    else:
        print("Таблица Users уже существует")

    connection.commit()
    connection.close()
    print("Проверка и создание таблиц завершены")


# Вызываем функцию
ensure_database_tables()

# Функция для работы с БД
def get_all_products():
    with sqlite3.connect('my_database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT id, title, description, price, image_path FROM Products')
        products = cursor.fetchall()
        return products


# Инициализация бота и диспетчера
bot = Bot(token='7777')
storage = MemoryStorage()
dp = Dispatcher( storage=storage)

button = KeyboardButton(text="Информация")
button2 = KeyboardButton(text='Рассчитать')
button5 = KeyboardButton(text='Купить')
button1 = KeyboardButton(text='Регистрация')

kb = ReplyKeyboardMarkup(
    keyboard=[
        [button, button2],
        [button1, button5]
    ],
    resize_keyboard=True
)

button3 = InlineKeyboardButton(text='Рассчет нормы для женщин', callback_data='calories for women')
button6 = InlineKeyboardButton(text='Рассчет нормы для мужчин', callback_data='calories for men')
button4 = InlineKeyboardButton(text='Формула для женщин', callback_data='formula for women')
button7 = InlineKeyboardButton(text='Формула для мужчин', callback_data='formula for men')

kb2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [button3, button4],  # первый ряд с двумя кнопками
        [button6, button7]   # второй ряд с двумя кнопками
    ]
)

# Создаем кнопки
button8 = InlineKeyboardButton(text='Продукт1', callback_data='product_buying_1')
button9 = InlineKeyboardButton(text='Продукт2', callback_data='product_buying_2')
button10 = InlineKeyboardButton(text='Продукт3', callback_data='product_buying_3')
button11 = InlineKeyboardButton(text='Продукт4', callback_data='product_buying_4')
button12 = InlineKeyboardButton(text='Продукт5', callback_data='product_buying_5')

# Создаем клавиатуру с уже готовой строкой кнопок
buy_kb = InlineKeyboardMarkup(inline_keyboard=[[button8, button9, button10, button11, button12]])


# Определение состояний
class WomenState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class MenState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()

@dp.message(F.text == 'Рассчитать')
async def calculate_handler(message: Message):
    await message.answer('Выберите опцию:', reply_markup=kb2)


@dp.callback_query(F.data=='formula for women')
async def process_formula_women(callback_query: types.CallbackQuery):
    await callback_query.answer()
    formula_text = (
        "Формула расчета BMR для женщин:\n\n"
        "BMR = (10 × вес в кг) + (6.25 × рост в см) - (5 × возраст) - 161\n\n"
        "Эта формула Миффлина-Сан Жеора позволяет рассчитать базовый уровень метаболизма."
    )
    await callback_query.message.answer(formula_text)

@dp.callback_query(F.data=='formula for men')
async def process_formula_men(callback_query: types.CallbackQuery):
    await callback_query.answer()
    formula_text = (
        "Формула расчета BMR для мужчин:\n\n"
        "BMR = (10 × вес в кг) + (6.25 × рост в см) - (5 × возраст) + 5\n\n"
        "Эта формула Миффлина-Сан Жеора позволяет рассчитать базовый уровень метаболизма."
    )
    await callback_query.message.answer(formula_text)

# Для женщин
@dp.callback_query(F.data=='calories for women')
async def process_calories_women(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Введите свой возраст:')
    await state.set_state(WomenState.age)
    await call.answer()


@dp.message(WomenState.age,)
async def process_women_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if 10 <= age <= 100:
            await state.update_data(age=age)
            await message.answer("Введите свой рост в см:")
            await state.set_state(WomenState.growth)
        else:
            await message.answer("Пожалуйста, введите корректный возраст (от 10 до 100 лет).")
    except ValueError:
        await message.answer("Пожалуйста, введите возраст числом.")

@dp.message(WomenState.growth)
async def process_women_growth(message: types.Message, state: FSMContext):
    try:
        growth = int(message.text)
        if 140 <= growth <= 220:
            await state.update_data(growth=growth)
            await message.answer("Введите свой вес в кг:")
            await state.set_state(WomenState.weight)
        else:
            await message.answer("Пожалуйста, введите корректный рост (от 140 до 220 см).")
    except ValueError:
        await message.answer("Пожалуйста, введите рост числом.")

@dp.message(WomenState.weight)
async def send_calories_women(message: Message, state: FSMContext):
    try:
        # Проверка и сохранение веса
        weight_input = message.text
        weight = float(weight_input)
        if weight <= 0 or weight > 500:
            await message.answer("Пожалуйста, введите корректный вес (от 1 до 500 кг).")
            return

        # Убран лишний отступ здесь и ниже
        await state.update_data(weight=weight)
        data = await state.get_data()

        age = float(data["age"])
        growth = float(data["growth"])
        weight = float(data["weight"])

        # Расчет BMR для женщин
        calories = (10 * weight) + (6.25 * growth) - (5 * age) - 161

        await message.answer(f"Ваша базовая норма калорий (BMR): {round(calories)} ккал/день")
        # Исправлена опечатка replay_markup -> reply_markup
        await message.answer('Нажмите "Информация" для выбора продукта', reply_markup=kb)

    except ValueError:
        await message.answer("Пожалуйста, введите корректные числовые значения")

    finally:
        # Завершаем машину состояний
        await state.clear()



# Для мужчин
@dp.callback_query(F.data == 'calories for men')
async def process_men_age(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Введите свой возраст:')
    await state.set_state(MenState.age)
    await call.answer()


@dp.message(MenState.age)
async def process_men_growth(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0 or age > 120:
            await message.answer('Пожалуйста, введите корректный возраст (от 1 до 120 лет).')
            return

        await state.update_data(age=age)
        await message.answer('Введите свой рост:')
        await state.set_state(MenState.growth)
    except ValueError:
        await message.answer('Пожалуйста, введите возраст числом.')


@dp.message(MenState.growth)
async def process_men_weight(message: Message, state: FSMContext):
    try:
        growth = float(message.text)
        if growth < 50 or growth > 250:
            await message.answer('Пожалуйста, введите корректный рост в сантиметрах (от 50 до 250 см).')
            return

        await state.update_data(growth=growth)
        await message.answer('Введите свой вес:')
        await state.set_state(MenState.weight)
    except ValueError:
        await message.answer('Пожалуйста, введите рост числом в сантиметрах.')


@dp.message(MenState.weight)
async def send_calories_men(message: Message, state: FSMContext):
    try:
        # Проверка и сохранение веса
        weight_input = message.text
        weight = float(weight_input)
        if weight <= 0 or weight > 500:
            await message.answer("Пожалуйста, введите корректный вес (от 1 до 500 кг).")
            return

        await state.update_data(weight=weight)
        data = await state.get_data()

        age = float(data['age'])
        weight = float(data['weight'])
        height = float(data['growth'])

        # Формула для мужчин (формула Миффлина-Сан Жеора)
        calories = (10 * weight) + (6.25 * height) - (5 * age) + 5

        await message.answer(f"Ваша базовая норма калорий (BMR): {round(calories)} ккал/день")
        await message.answer('Нажмите "Информация" для выбора продукта', reply_markup=kb)

    except ValueError:
        await message.answer("Пожалуйста, введите корректные числовые значения")

    finally:
        # Завершаем машину состояний
        await state.clear()


@dp.message(F.text == 'Регистрация')
async def sign_up(message: Message, state: FSMContext):
    # Устанавливаем состояние для ввода имени пользователя
    await state.set_state(RegistrationState.username)
    await message.answer('Введите свое имя: (только латинский алфавит)')


@dp.message(RegistrationState.username)
async def set_username(message: Message, state: FSMContext):
    if is_included(message.text):  # Проверяем, существует ли пользователь
        await message.answer("Пользователь существует, введите другое имя")
        await state.set_state(RegistrationState.username)
        return

    # Сохраняем имя пользователя
    await state.update_data(username=message.text)

    await state.set_state(RegistrationState.email)
    await message.answer("Введите свой email:")


@dp.message(RegistrationState.email)
async def set_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)

    await state.set_state(RegistrationState.age)
    await message.answer("Введите свой возраст:")


@dp.message(RegistrationState.age)
async def set_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)

    # Получаем все данные и добавляем пользователя
    data = await state.get_data()
    add_user(
        username=data['username'],
        email=data['email'],
        age=data['age']
    )

    await message.answer("Регистрация успешно завершена!\n"
                         "Нажмите 'Рассчитать' для расчета нормы калорий",
                         reply_markup=kb)
    await state.clear()


@dp.message(F.text == "Информация")
async def info(message: Message):
    # Создаем InputFile из пути к файлу
    photo = FSInputFile("files/collage.jpg")

    # Если texts14.about - это словарь, извлекаем из него текст
    if isinstance(texts14.about, dict):
        caption = texts14.about.get('description', 'Информация о продуктах')
    else:
        caption = str(texts14.about)

    # Отправляем фото с подписью
    await message.answer_photo(
        photo=photo,
        caption=caption
    )
    await message.answer(F"Нажмите 'Купить' для подбора и приобретения продукта")


# Пример с ограничением количества продуктов
@dp.message(F.text == "Купить")
async def show_catalog(message: Message):
    products = get_all_products()
    # Ограничиваем до 5 продуктов за раз
    for product in products[:5]:
        id, title, description, price, image_path = product
        try:
            photo = FSInputFile(image_path)
            await message.answer_photo(
                photo=photo,
                caption=f"Товар: {title}\n"
                        f"Описание: {description}\n"
                        f"Цена: {price} руб."
            )
        except FileNotFoundError:
            await message.answer(
                f"Товар: {title}\n"
                f"Описание: {description}\n"
                f"Цена: {price} руб.\n"
                f"(Изображение недоступно)"
            )

    await message.answer("Выберите продукт для покупки:", reply_markup=buy_kb)


@dp.callback_query(lambda c: c.data.startswith('product_buying'))
async def process_buying(call: CallbackQuery):
    await send_confirm_message(call)

async def send_confirm_message(call: CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, "Вы успешно приобрели продукт!")


@dp.message(Command("start"))
async def second_message(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.answer('Привет! Я бот, помогающий твоему здоровью!\n'
                         'Нажмите кнопку "Регистрация" ',
                         reply_markup=kb)

@dp.message(~F.text.in_(['/start', 'Информация', 'Рассчитать', 'Купить']))
async def first_message(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} отправил: {message.text}")
    await message.answer('Введите команду /start, чтобы начать общение ')


async def main():
    logger.info('Запуск бота....')

    # Выводим информацию о боте
    try:
        bot_info = await bot.get_me()
        logger.info(f"Бот @{bot_info.username} успешно подключен")
    except Exception as e:
        logger.error(f"Ошибка при получении информации о боте: {e}")
        return

        # Запускаем поллинг
    try:
        logger.info("Начинаем поллинг...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске поллинга: {e}")

    #await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    init_db()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")




