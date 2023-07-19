from config import TOKEN
from aiogram import Bot,Dispatcher,executor,types
import mysql.connector
from mysql.connector import Error
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram
import os
import asyncio
import io

# Создаем объект хранилища состояний
storage = MemoryStorage()

bot = Bot(TOKEN)
dp = Dispatcher(bot,storage=storage)


# Определение состояний FSM
class AddCarState(StatesGroup):
    mark = State()
    model = State()
    year = State()
    rest = State()
    price = State()
    image1 = State()
    image2 = State()
    image3 = State()
    image4 = State()
    description = State()

# Список администраторов (ID пользователей Telegram)
admin_ids = [5455171373, 742904205]  # Замените ID на фактические ID ваших администраторов

# Подключение к базе данных MySQL
conn = mysql.connector.connect(
            host='localhost',
            database='cars',
            user='root',
            password='chinchaev007'
        )
cursor = conn.cursor()

# Функция для создания подключения к базе данных MySQL
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='cars',
            user='root',
            password='chinchaev007'
        )
        print('Connection to MySQL successful')
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

# Функция для создания таблицы моделей авто в базе данных MySQL
def create_car_models_table(connection):
    try:
        cursor = connection.cursor()
        create_table_query = '''CREATE TABLE IF NOT EXISTS car_models (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                mark VARCHAR(255) NOT NULL,
                                model VARCHAR(255) NOT NULL,
                                year INT,
                                restyling BOOLEAN,
                                price DECIMAL(10, 2),
                                image1 TEXT,
                                image2 TEXT,
                                image3 TEXT,
                                image4 TEXT,
                                description TEXT
                                )'''
        cursor.execute(create_table_query)
        connection.commit()
        print('Car models table created successfully')
    except Error as e:
        print(f"The error '{e}' occurred")

# Функция для получения моделей авто из базы данных
def get_car_models():
    connection = create_connection()
    try:
        cursor = connection.cursor()
        select_query = "SELECT DISTINCT  mark FROM car_models"
        cursor.execute(select_query)
        car_models = cursor.fetchall()
        return car_models
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection:
            connection.close()


def get_car_models_by_brand(brand):
    connection = create_connection()
    try:
        cursor = connection.cursor()
        select_query = "SELECT id,model,year,restyling,price FROM car_models WHERE mark = %s"
        cursor.execute(select_query, (brand,))
        car_models = cursor.fetchall()
        return car_models
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection:
            connection.close()

def get_car_models_by_model(id):
    connection = create_connection()
    try:
        cursor = connection.cursor()
        select_query = "SELECT id,model,year,restyling,price FROM car_models WHERE id = %s"
        cursor.execute(select_query, (id,))
        car_models = cursor.fetchall()
        return car_models
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection:
            connection.close()

# Функция для сохранения автомобиля в базе данных
def save_car_to_database(mark, model, year, restyling, price):
    connection = create_connection()
    try:
        cursor = connection.cursor()

        # Подготовка SQL-запроса для вставки данных автомобиля в таблицу
        insert_query = '''INSERT INTO car_models (mark, model, year, restyling, price)
                          VALUES (%s, %s, %s, %s, %s)'''
        
        # Параметры для SQL-запроса
        params = (mark, model, year, restyling, price)

        # Выполнение SQL-запроса
        cursor.execute(insert_query, params)
        connection.commit()
        
        print('Car added to database successfully')
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection:
            connection.close()

@dp.message_handler(commands=['start'])
async def start(message:types.Message):
    if message.from_user.id in admin_ids:
        mark_admin = types.InlineKeyboardMarkup()
        btn_admin_1 = types.InlineKeyboardButton('Мои чаты',callback_data='chats')
        btn_admin_2 = types.InlineKeyboardButton('Управление каталогом',callback_data='change_catalog')
        btn_admin_3 = types.InlineKeyboardButton('Управление FAQ',callback_data='change_faq')
        mark_admin.add(btn_admin_1,btn_admin_2)
        mark_admin.add(btn_admin_3)
        await bot.send_message(message.chat.id,'Выберите опцию',reply_markup=mark_admin)


    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Написать в лс',callback_data='ls')
        btn2 = types.InlineKeyboardButton('Каталог авто',callback_data='catalog_auto')
        btn3 = types.InlineKeyboardButton('Ответы на вопросы',callback_data='answers')
        markup.add(btn1,btn2)
        markup.add(btn3)
        await bot.send_message(message.chat.id,'Выберите опцию',reply_markup=markup)
        print(message.from_user.id)



@dp.callback_query_handler(lambda c: c.data == 'change_catalog')
async def change_cat(query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Вывести весь список авто',callback_data='display_cars_admin')
    btn2 = types.InlineKeyboardButton('Назад',callback_data='back_admin_1')

    keyboard.add(btn1,btn2)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'back_admin_1')
async def channge_cat(query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Вывести весь список авто',callback_data='display_cars_admin')
    btn2 = types.InlineKeyboardButton('Назад',callback_data='back_admin_1')

    keyboard.add(btn1,btn2)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)



@dp.callback_query_handler(lambda c: c.data =='display_cars_admin')
async def display_carss_admin(query:types.CallbackQuery):
    if query.from_user.id in admin_ids:
            markup = types.InlineKeyboardMarkup()

    car_models = get_car_models()  # Получаем модели авто из базы данных

    # Создаем кнопки для каждой модели авто
    for car_model in car_models:
        btn = types.InlineKeyboardButton(car_model[0], callback_data=f'liist_cars_{car_model[0]}')
        markup.add(btn)
    btn2 = types.InlineKeyboardButton('Назад',callback_data='back_admin_1')
    btn3 = types.InlineKeyboardButton('Добавить авто',callback_data='add_auto')
    markup.add(btn2,btn3)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data.startswith('liist_cars_'))
async def list_cars(query: types.CallbackQuery):
    brand = query.data  # Get the selected car brand
    brand = brand[11:]
    
    car_models = get_car_models_by_brand(brand)  # Get car models for the selected brand
    markup = types.InlineKeyboardMarkup()
    if car_models:
        models_text = "Модели автомобилей:"
        for car_model in car_models:
            if car_model[2]:
                btn = types.InlineKeyboardButton(f"{brand} {car_model[1]} {car_model[2]} | Рейсталинг - {car_model[4]}",callback_data=f'models_{car_model[0]}')
                markup.add(btn)
            else:
                btn = types.InlineKeyboardButton(f"{brand} {car_model[1]} {car_model[2]}  - {car_model[4]}",callback_data=f'models_{car_model[0]}')
                markup.add(btn)
        btn2 = types.InlineKeyboardButton('Назад',callback_data='back_admin_1')
        markup.add(btn2)
    else:
        models_text = "Нет доступных моделей для выбранной марки автомобиля."

    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data.startswith('models_'))
async def crud_model(query:types.CallbackQuery):
    model = query.data[7:]
    print(model)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Добавить фото',callback_data=f'add_image_{model}')
    btn6 = types.InlineKeyboardButton('Добавить описание',callback_data=f'add_descp_{model}')
    btn2 = types.InlineKeyboardButton('Удалить модель',callback_data=f'delete_model_{model}')
    btn4 = types.InlineKeyboardButton('Назад',callback_data='back_models')
    btn5 = types.InlineKeyboardButton('Посмотреть карточку',callback_data=f'view_car_{model}')
    markup.add(btn1,btn2)
    markup.add(btn5,btn6)
    markup.add(btn4)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)


import os

image_folder = 'images'

@dp.callback_query_handler(lambda c: c.data.startswith('view_car_'))
async def view_car_admin(query: types.CallbackQuery):
    # Получаем идентификатор модели авто из query.data или из другого источника
    model_id = query.data[9:]  # Предполагается, что идентификатор модели передается в query.data

    # Получаем информацию о модели авто из базы данных
    select_query = '''SELECT * FROM car_models WHERE id = %s'''
    params = (model_id,)
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(select_query, params)
        model = cursor.fetchone()
        if model:
            # Формируем информацию о модели авто
            car_info = f"Марка: {model[1]}\nМодель: {model[2]}\nГод: {model[3]}\nРестайлинг: {model[4]}\nЦена: {model[5]}"

            # Создаем список с медиа-объектами изображений
            media = []
            for i in range(6, 10):
                if model[i]:
                    image_path = os.path.join(image_folder, model[i])
                    media.append(types.InputMediaPhoto(media=image_path))

            # Добавляем информацию о модели как текстовое сообщение
            media.append(types.InputMediaDocument(media=car_info, parse_mode='Markdown'))

            # Отправляем все изображения и информацию о модели в одном сообщении
            await bot.send_media_group(query.message.chat.id, media)
        else:
            await bot.send_message(query.message.chat.id, "Модель авто не найдена")
    except Error as e:
        print(f"The error '{e}' occurred")




@dp.callback_query_handler(lambda c: c.data.startswith('add_image_'))
async def add_description(query: types.CallbackQuery):
    # Получаем идентификатор модели авто из query.data или из другого источника
    model_id = query.data[10:]  # Предполагается, что идентификатор модели передается в query.data
    print(model_id)

    # Запрашиваем у пользователя 4 фото для модели
    await query.answer(f"Пожалуйста, отправьте 4 фото для модели с идентификатором {model_id}")

    # Создайте обработчик для получения фотографий и описания от пользователя
    @dp.message_handler(content_types=types.ContentType.PHOTO)
    async def handle_photos(message: types.Message):
        # Получите фотографии из сообщения
        photos = message.photo[-4:]  # Получите последние 4 фотографии
        
            # Загрузите фотографии в папку images и сохраните пути к ним в базе данных
        try:
            image_paths = []
            for index, photo in enumerate(photos):
                    
                image_path = f'images/{model_id}_{index + 1}.jpg'  # Используйте уникальный идентификатор для имени файла
                await photo.download(image_path)
                image_paths.append(image_path)
        except:
            await message.answer('Ошибка при загрузке')
                # Обновите запись в базе данных, добавив пути к фотографиям
        update_query = '''UPDATE car_models
                                SET image1 = %s, image2 = %s, image3 = %s, image4 = %s
                                WHERE id = %s'''
        params = (image_paths[0], image_paths[1], image_paths[2], image_paths[3], model_id)

        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(update_query, params)
            connection.commit()
            await bot.send_message(message.chat.id, 'Фотографии успешно добавлены')
        except Error as e:
            await message.answer('Ошибка при загрузке')



    # Установите обработчик для получения фотографий от пользователя
    dp.register_message_handler(handle_photos, content_types=types.ContentType.PHOTO)


@dp.callback_query_handler(lambda c: c.data.startswith('add_descp_'))
async def descpription_admin(query:types.CallbackQuery):
    # Получаем идентификатор модели авто из query.data или из другого источника
    model_id = query.data[10:]  # Предполагается, что идентификатор модели передается в query.data
    print(model_id)

    # Запрашиваем у пользователя 4 фото для модели
    await query.answer(f"Пожалуйста, отправьте описание для модели машины {model_id}")

    @dp.message_handler(content_types=types.ContentType.TEXT)
    async def handle_photos(message: types.Message):
        text = message.text

        update_query = '''UPDATE car_models
                                SET description = %s
                                WHERE id = %s'''
        params = (text, model_id)

        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(update_query, params)
            connection.commit()
            await bot.send_message(message.chat.id, 'Описание успешно добавлено')
            
        except Error as e:
            await message.answer('Ошибка при загрузке')


    dp.register_message_handler(handle_photos, content_types=types.ContentType.TEXT)


@dp.callback_query_handler(lambda c: c.data.startswith('delete_model_'))
async def delete_model(query: types.CallbackQuery):
    # Получаем идентификатор модели авто из query.data или из другого источника
    model_id = query.data[13:]  # Предполагается, что идентификатор модели передается в query.data
    print(model_id)
    connection = create_connection()
    try:
        cursor = connection.cursor()
        delete_query = '''DELETE FROM car_models WHERE id = %s'''
        params = (model_id,)
        cursor.execute(delete_query, params)
        connection.commit()
        await query.answer("Модель успешно удалена")

    except Error as e:
        await query.answer(f'Ошибка при удалении: {e}')
    finally:
        if connection:
            connection.close()

    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Вывести весь список авто', callback_data='display_cars_admin')
    btn2 = types.InlineKeyboardButton('Назад', callback_data='back_admin_1')

    keyboard.add(btn1, btn2)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)



@dp.callback_query_handler(lambda c: c.data =='back_models' )
async def back_mod(query: types.CallbackQuery):
    brand = query.data  # Get the selected car brand
    brand = brand[11:]
    
    car_models = get_car_models_by_brand(brand)  # Get car models for the selected brand
    markup = types.InlineKeyboardMarkup()
    if car_models:
        models_text = "Модели автомобилей:"
        for car_model in car_models:
            if car_model[2]:
                btn = types.InlineKeyboardButton(f"{brand} {car_model[0]} {car_model[1]} | Рейсталинг - {car_model[3]}",callback_data=f'models_{car_model[0]}')
                markup.add(btn)
            else:
                btn = types.InlineKeyboardButton(f"{brand} {car_model[0]} {car_model[1]}  - {car_model[3]}",callback_data=f'models_{car_model[0]}')
                markup.add(btn)
        btn2 = types.InlineKeyboardButton('Назад',callback_data='back1')
        markup.add(btn2)
    else:
        models_text = "Нет доступных моделей для выбранной марки автомобиля."

    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)



@dp.callback_query_handler(lambda c: c.data == 'add_auto')
async def add_car(query: types.CallbackQuery):
    if query.from_user.id in admin_ids:
        await AddCarState.mark.set()  # Переход в состояние ожидания марки автомобиля
        await bot.send_message(query.from_user.id, "Начинаю процесс добавления автомобиля...")
        await bot.send_message(query.from_user.id, "Введите марку автомобиля:")

@dp.message_handler(state=AddCarState.mark)
async def add_model(message: types.CallbackQuery, state: FSMContext):

    if message.from_user.id in admin_ids:
        await state.update_data(mark=message.text)  # Сохраняем значение модели автомобиля
        await message.answer('Напишите модель автомобиля')
        await AddCarState.next()

@dp.message_handler(state=AddCarState.model)
async def add_year(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_ids:
        await state.update_data(model=message.text)  # Сохраняем значение модели автомобиля
        await bot.send_message(message.from_user.id, "Введите год выпуска автомобиля:")
        await AddCarState.year.set()  # Переход в состояние ожидания года выпуска автомобиля

@dp.message_handler(state=AddCarState.year)
async def add_restyling(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_ids:
        try:
            year = int(message.text)  # Преобразуем год в целое число
            await state.update_data(year=year)  # Сохраняем значение года выпуска автомобиля
            await bot.send_message(message.from_user.id, "Введите информацию о рестайлинге (да/нет):")
            await AddCarState.next()  # Переход в состояние ожидания информации о рестайлинге
        except ValueError:
            await bot.send_message(message.from_user.id, "Неверный формат года. Попробуйте еще раз.")


@dp.message_handler(state=AddCarState.rest)
async def add_price(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_ids:
        try:
            restyling = bool(message.text.lower() == 'да')  # Преобразуем информацию о рестайлинге в булево значение
            await state.update_data(rest=restyling)  # Сохраняем значение информации о рестайлинге
            await bot.send_message(message.from_user.id, "Введите цену автомобиля:")
            await AddCarState.next()  # Переход в состояние ожидания цены автомобиля
        except ValueError:
            await bot.send_message(message.from_user.id, "Неверный формат информации о рестайлинге. Попробуйте еще раз.")






@dp.message_handler(state=AddCarState.price)
async def save_car_data(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_ids:
        await state.update_data(price= int(message.text))  # Сохраняем значение описания автомобиля
        data = await state.get_data()  # Получаем сохраненные данные из состояния FSM
        mark = data['mark']
        model = data['model']
        year = data['year']
        restyling = data['rest']
        price = data['price']

        # Вызываем функцию сохранения данных в базу данных
        save_car_to_database(mark, model, year, restyling, price)

        await state.finish()
        await bot.send_message(message.from_user.id, "Автомобиль успешно добавлен в базу данных.")


@dp.callback_query_handler(lambda c: c.data == 'back_admin_1')
async def go_back_admin_1(query: types.CallbackQuery):
    mark_admin = types.InlineKeyboardMarkup()
    btn_admin_1 = types.InlineKeyboardButton('Мои чаты',callback_data='chats')
    btn_admin_2 = types.InlineKeyboardButton('Управление каталогом',callback_data='change_catalog')
    btn_admin_3 = types.InlineKeyboardButton('Управление FAQ',callback_data='change_faq')
    mark_admin.add(btn_admin_1,btn_admin_2)
    mark_admin.add(btn_admin_3)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=mark_admin)

@dp.callback_query_handler(lambda c: c.data == 'ls')
async def handle_callback_query(query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Чат с админом',url='https://t.me/tiqtim')
    btn2 = types.InlineKeyboardButton('Назад',callback_data='back1')
    keyboard.add(btn1,btn2)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)




@dp.callback_query_handler(lambda c: c.data == 'catalog_auto')
async def cars(query: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()

    car_models = get_car_models()  # Получаем модели авто из базы данных

    # Создаем кнопки для каждой модели авто
    for car_model in car_models:
        btn = types.InlineKeyboardButton(car_model[0], callback_data=f'spisok_cars_{car_model[0]}')
        markup.add(btn)
    btn2 = types.InlineKeyboardButton('Назад',callback_data='back1')
    markup.add(btn2)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith('spisok_cars_'))
async def list_cars(query: types.CallbackQuery):
    brand = query.data  # Get the selected car brand
    brand = brand[12:]
    print(brand)
    car_models = get_car_models_by_brand(brand)  # Get car models for the selected brand
    markup = types.InlineKeyboardMarkup()
    if car_models:
        models_text = "Модели автомобилей:"
        for car_model in car_models:
            if car_model[2]:
                btn = types.InlineKeyboardButton(f"{brand} {car_model[0]} {car_model[1]} | Рейсталинг - {car_model[4]}",callback_data=f'u_models_{car_model[0]}')
                markup.add(btn)
            else:
                btn = types.InlineKeyboardButton(f"{brand} {car_model[0]} {car_model[1]}  - {car_model[4]}",callback_data=f'u_models_{car_model[0]}')
                markup.add(btn)
        btn2 = types.InlineKeyboardButton('Назад',callback_data='back1')
        markup.add(btn2)
    else:
        await bot.send_message(query.message.chat.id,'Нет моделей для данной марки')

    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)



@dp.callback_query_handler(lambda c: c.data == 'back2')
async def go_back_2(query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Назад',callback_data='back1')
    btn2 = types.InlineKeyboardButton('BMW',callback_data='bmw')
    btn3 = types.InlineKeyboardButton('Всего 8-12 марок авто',callback_data='marks')
    keyboard.add(btn1,btn2)
    keyboard.add(btn3)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'back1')
async def go_back_3(query: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Написать в лс',callback_data='ls')
    btn2 = types.InlineKeyboardButton('Каталог авто',callback_data='catalog_auto')
    btn3 = types.InlineKeyboardButton('Ответы на вопросы',callback_data='answers')
    markup.add(btn1,btn2)
    markup.add(btn3)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)




executor.start_polling(dp)

if __name__ == '__main__':
    connection = create_connection()  # Создание подключения к базе данных
    create_car_models_table(connection)  # Создание таблицы моделей авто
    executor.start_polling(dp)