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
from base import *
from state import *
import aiohttp
from functools import partial
from PIL import Image
# Создаем объект хранилища состояний
storage = MemoryStorage()

bot = Bot(TOKEN)
dp = Dispatcher(bot,storage=storage)




# Список администраторов (ID пользователей Telegram)
admin_ids = [5455171373, 742904205,907703822]  # Замените ID на фактические ID ваших администраторов
folder_name = 'SearchCar_bot/images'
folder_path = os.path.abspath(folder_name)
if not os.path.exists("images"):
    os.makedirs("images")
#-------------------------------------------START-------------------------------------------
@dp.message_handler(commands=['start'])
async def start(message:types.Message):
    if message.from_user.id in admin_ids:
        mark_admin = types.InlineKeyboardMarkup()
        btn_admin_1 = types.InlineKeyboardButton('Мои чаты',url='https://t.me/+SOGuI6Qjp9wyYjRi')
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


#------------------------------------УПРАВЛЕНИЕ FAQ-----------------------------------------
@dp.callback_query_handler(lambda c: c.data == 'change_faq')
async def questions_admin(query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Редактировать вопрос 1',callback_data='quest_first')
    btn2 = types.InlineKeyboardButton('Редактировать вопрос 2',callback_data='quest_second')
    btn3 = types.InlineKeyboardButton('Редактировать вопрос 3',callback_data='quest_third')
    btn4 = types.InlineKeyboardButton('Назад',callback_data='back_admin_1')
    keyboard.add(btn1)
    keyboard.add(btn2)
    keyboard.add(btn3)
    keyboard.add(btn4)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)

#-----------------------------------------ВОПРОСЫ---------------------------------------------

@dp.callback_query_handler(lambda c: c.data.startswith('quest'))
async def admin_quest1(query: types.CallbackQuery):
    qv = query.data

    current_answer = get_quest_by_id(qv)
    if current_answer:
        await bot.send_message(query.message.chat.id, f'Текущий ответ на вопрос\n{current_answer[0][0]}')
    else:
        await bot.send_message(query.message.chat.id, f'Ответ на вопрос не найден')

    # Ask the admin to enter the new answer
    
    await bot.send_message(query.message.chat.id, f'Можно внести новый ответ или добавить ответ на вопрос {qv}:')
    @dp.message_handler(content_types=types.ContentType.TEXT)
    async def handle_text(message: types.Message):
        text = message.text

        update_quest_by_id(qv,  text)

        await bot.send_message(message.chat.id, f'Ответ на вопрос {qv} обновлен: {text}')
        keyboard = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('Назад',callback_data='back_admin_1')
        keyboard.add(btn)
        await bot.send_message(message.chat.id,'Выберите опцию',reply_markup=keyboard)
    
    dp.register_message_handler(handle_text, content_types=types.ContentType.TEXT)

#-------------------------------------------------УПРАВЛЕНИЕ КАТАЛОГОМ ----------------------------------------------

@dp.callback_query_handler(lambda c: c.data == 'change_catalog')
async def change_cat(query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Вывести весь список авто',callback_data='display_cars_admin')
    btn2 = types.InlineKeyboardButton('Назад',callback_data='back_admin_1')

    keyboard.add(btn1,btn2)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)

#--------------------------------------------------------Назад к меню каталога------------------------------------

@dp.callback_query_handler(lambda c: c.data == 'back_admin_1')
async def channge_cat(query: types.CallbackQuery):
    
    mark_admin = types.InlineKeyboardMarkup()
    btn_admin_1 = types.InlineKeyboardButton('Мои чаты',url='https://t.me/+SOGuI6Qjp9wyYjRi')
    btn_admin_2 = types.InlineKeyboardButton('Управление каталогом',callback_data='change_catalog')
    btn_admin_3 = types.InlineKeyboardButton('Управление FAQ',callback_data='change_faq')
    mark_admin.add(btn_admin_1,btn_admin_2)
    mark_admin.add(btn_admin_3)

    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=mark_admin)

#-------------------------------------------Отобразить марки админ-----------------------------------

@dp.callback_query_handler(lambda c: c.data =='display_cars_admin')
async def display_carss_admin(query:types.CallbackQuery):
    if query.from_user.id in admin_ids:
            markup = types.InlineKeyboardMarkup()

    car_models = get_car_models()  # Получаем модели авто из базы данных

    # Создаем кнопки для каждой модели авто
    for car_model in car_models:
        btn = types.InlineKeyboardButton(car_model[0], callback_data=f'liist_cars_{car_model[0]}')
        markup.add(btn)
    btn2 = types.InlineKeyboardButton('Назад',callback_data='change_catalog')
    btn3 = types.InlineKeyboardButton('Добавить авто',callback_data='add_auto')
    markup.add(btn2,btn3)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)

#------------------------Отобразить модели------------------------------------------------------

@dp.callback_query_handler(lambda c: c.data.startswith('liist_cars_'))
async def list_cars(query: types.CallbackQuery):
    brand = query.data  # Get the selected car brand
    brand = brand[11:]
    
    car_models = get_car_models_by_brand(brand)  # Get car models for the selected brand
    print(car_models)
    markup = types.InlineKeyboardMarkup()
    if car_models:
        models_text = "Модели автомобилей:"
        for car_model in car_models:
            
            btn = types.InlineKeyboardButton(f" {car_model[1]} {car_model[2]} {car_model[3]} - {car_model[4]}",callback_data=f'models_{car_model[0]}')
            markup.add(btn)

        btn2 = types.InlineKeyboardButton('Назад',callback_data='display_cars_admin')
        markup.add(btn2)
    else:
        models_text = "Нет доступных моделей для выбранной марки автомобиля."

    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)

#---------------------------------------Определенная модель CRUD---------------------------------

@dp.callback_query_handler(lambda c: c.data.startswith('models_'))
async def crud_model(query:types.CallbackQuery):
    model = query.data[7:]
    car = get_all_by_id(model)
    print(car[0][9])
    info = []
    if car[0][9]==None:
        info.append('Добавить описание')
        info.append('add_descp')
    else:
        info.append('Редактировать описание')
        info.append('change_descp')
    print(info)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Добавить фото',callback_data=f'add_image_{model}')
    btn6 = types.InlineKeyboardButton(f'{info[0]}',callback_data=f'{info[1]}_{model}')
    btn2 = types.InlineKeyboardButton('Удалить модель',callback_data=f'delete_model_{model}')
    btn4 = types.InlineKeyboardButton('Назад',callback_data=f'display_cars_admin')
    btn5 = types.InlineKeyboardButton('Посмотреть карточку',callback_data=f'view_car_{model}')
    markup.add(btn1,btn2)
    markup.add(btn5,btn6)
    markup.add(btn4)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)

#------------------Добавить описание--------------------------

@dp.callback_query_handler(lambda c: c.data.startswith('add_descp_'))
async def descpription_admin(query: types.CallbackQuery,state:FSMContext):
    model = query.data[10:]  # идентификатор модели передается в query.data
    print(model)
    car = get_all_by_id(model)
    # Запрашиваем у пользователя описание для модели
    await query.answer(f"Пожалуйста, отправьте описание для модели машины {model}")
    await DescriptionForm.add_description.set() 
    await state.update_data(model_id=model)

@dp.message_handler(state=DescriptionForm.add_description, content_types=types.ContentType.TEXT)
async def handle_add_description(message: types.Message, state: FSMContext):
    text = message.text
    async with state.proxy() as data:
        model_id = data['model_id']  # Retrieve the model_id from the FSMContext

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

    await state.finish()  # Завершаем состояние после добавления описания

    car = get_all_by_id(model_id)
    print(car[0][9])
    info = []
    if car[0][9] is None:
        info.append('Добавить описание')
        info.append('add_descp')
    else:
        info.append('Редактировать описание')
        info.append('change_descp')
    print(info)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Добавить фото', callback_data=f'add_image_{model_id}')
    btn6 = types.InlineKeyboardButton(f'{info[0]}', callback_data=f'{info[1]}_{model_id}')
    btn2 = types.InlineKeyboardButton('Удалить модель', callback_data=f'delete_model_{model_id}')
    btn4 = types.InlineKeyboardButton('Назад', callback_data=f'display_cars_admin')
    btn5 = types.InlineKeyboardButton('Посмотреть карточку', callback_data=f'view_car_{model_id}')
    markup.add(btn1, btn2)
    markup.add(btn5, btn6)
    markup.add(btn4)

    await bot.send_message(message.chat.id, 'Выберите опцию', reply_markup=markup)



@dp.callback_query_handler(lambda c: c.data.startswith('change_descp_'))
async def descpription_admin(query: types.CallbackQuery,state:FSMContext):
    model_id = query.data[13:]  # Extract the model_id from query.data
    print(f'Ид  cars {model_id}')
    car = get_all_by_id(model_id)

    await bot.send_message(query.message.chat.id, f'Вот описание под машину\n {car[0][9]}')

    await bot.send_message(query.message.chat.id, 'Отправьте новое описание машины')
    await DescriptionForm.edit_description.set()  # Set the state to edit_description

    # Save the model_id in the state to be used in the handle_edit_description function
    await state.update_data(model_id=model_id)

@dp.message_handler(state=DescriptionForm.edit_description, content_types=types.ContentType.TEXT)
async def handle_edit_description(message: types.Message, state: FSMContext):
    text = message.text
    async with state.proxy() as data:
        model_id = data['model_id']  # Retrieve the model_id from the FSMContext

    update_query = '''UPDATE car_models
                      SET description = %s
                      WHERE id = %s'''
    params = (text, model_id)
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(update_query, params)
        connection.commit()
        await bot.send_message(message.chat.id, 'Описание успешно изменено')
    except Error as e:
        await message.answer('Ошибка при загрузке')

    await state.finish()  # Завершаем состояние после редактирования описания

    car = get_all_by_id(model_id)
    print(car[0][9])
    info = []
    if car[0][9] is None:
        info.append('Добавить описание')
        info.append('add_descp')
    else:
        info.append('Редактировать описание')
        info.append('change_descp')
    print(info)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Добавить фото', callback_data=f'add_image_{model_id}')
    btn6 = types.InlineKeyboardButton(f'{info[0]}', callback_data=f'{info[1]}_{model_id}')
    btn2 = types.InlineKeyboardButton('Удалить модель', callback_data=f'delete_model_{model_id}')
    btn4 = types.InlineKeyboardButton('Назад', callback_data=f'display_cars_admin')
    btn5 = types.InlineKeyboardButton('Посмотреть карточку', callback_data=f'view_car_{model_id}')
    markup.add(btn1, btn2)
    markup.add(btn5, btn6)
    markup.add(btn4)

    await bot.send_message(message.chat.id, 'Выберите опцию', reply_markup=markup)

#-------------------------Просмотреть машины админ--------------------------------------------

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
            car_info = f"Марка: {model[1]}\nМодель: {model[2]}\nГод: {model[3]}\nЦена: {model[4]}"
            # Создаем список с медиа-объектами изображений
            media = []
            if model[5]:
                for i in range(5, 9):
                    if model[i]:
                        image_path = model[i]
                        photo = types.InputFile(image_path)
                        media.append(types.InputMediaPhoto(media=photo))
                # Отправляем изображения модели в чат одним сообщением
                await bot.send_media_group(query.message.chat.id, media)


            # Отправляем оставшуюся информацию о модели во втором сообщении
            await bot.send_message(query.message.chat.id, car_info)

            # Отправляем описание модели в чат, если оно есть
            if model[9]:
                description = model[9]
                await bot.send_message(query.message.chat.id, f"Описание: {description}")
            

        else:
            await bot.send_message(query.message.chat.id, "Модель авто не найдена")
            model = query.data[7:]

    except Error as e:
        print(f'Error {e}')
    car = get_all_by_id(model_id)
    print(car[0][9])
    info = []

    if car[0][9]==None:
        info.append('Добавить описание')
        info.append('add_descp')
    else:
        info.append('Редактировать описание')
        info.append('change_descp')
    print(info)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Добавить фото',callback_data=f'add_image_{model_id}')
    btn6 = types.InlineKeyboardButton(f'{info[0]}',callback_data=f'{info[1]}_{model_id}')
    btn2 = types.InlineKeyboardButton('Удалить модель',callback_data=f'delete_model_{model_id}')
    btn4 = types.InlineKeyboardButton('Назад',callback_data=f'display_cars_admin')
    btn5 = types.InlineKeyboardButton('Посмотреть карточку',callback_data=f'view_car_{model_id}')
    markup.add(btn1,btn2)
    markup.add(btn5,btn6)
    markup.add(btn4)
    await bot.send_message(query.message.chat.id,'Выберите опцию',reply_markup=markup)


#---------------------------------------------Добавить изображение для машины-------------------------


# Функция для асинхронного скачивания и сохранения фотографии
photos = []
@dp.callback_query_handler(lambda c: c.data.startswith('add_image_'))
async def add_description(query: types.CallbackQuery, state: FSMContext):
    model_id = query.data[10:]
    await query.answer(f"Пожалуйста, отправьте 4 фото для модели с идентификатором {model_id}")

    # Clear any previous photo list and set the model_id in the FSMContext
    photos.clear()
    await state.update_data(model_id=model_id)

    # Set the initial state to photo_1 for the first photo
    await AddPhotosState.photo_1.set()

@dp.message_handler(state=AddPhotosState.photo_1, content_types=types.ContentType.PHOTO)
@dp.message_handler(state=AddPhotosState.photo_2, content_types=types.ContentType.PHOTO)
@dp.message_handler(state=AddPhotosState.photo_3, content_types=types.ContentType.PHOTO)
@dp.message_handler(state=AddPhotosState.photo_4, content_types=types.ContentType.PHOTO)
async def handle_photo_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        model_id = data['model_id']  # Retrieve the model_id from the FSMContext

    if len(photos) < 4:
        photos.append(message.photo[-1])  # Save the last photo sent (with the highest quality)

    # Set the next state for the next photo
    if len(photos) == 1:
        await AddPhotosState.photo_2.set()
    elif len(photos) == 2:
        await AddPhotosState.photo_3.set()
    elif len(photos) == 3:
        await AddPhotosState.photo_4.set()
    else:
        # If there are no more states, it means all 4 photos have been received
        # Process the photos, save them, and update the database
        downloaded_images = await process_photos(photos, model_id)
        await update_database_with_images(downloaded_images, model_id)

        await state.finish()
        await bot.send_message(message.chat.id,'Фотографии успещно добавлены')
        car = get_all_by_id(model_id)
        print(car[0][9])
        info = []

        if car[0][9]==None:
            info.append('Добавить описание')
            info.append('add_descp')
        else:
            info.append('Редактировать описание')
            info.append('change_descp')
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Добавить фото',callback_data=f'add_image_{model_id}')
        btn6 = types.InlineKeyboardButton(f'{info[0]}',callback_data=f'{info[1]}_{model_id}')
        btn2 = types.InlineKeyboardButton('Удалить модель',callback_data=f'delete_model_{model_id}')
        btn4 = types.InlineKeyboardButton('Назад',callback_data=f'display_cars_admin')
        btn5 = types.InlineKeyboardButton('Посмотреть карточку',callback_data=f'view_car_{model_id}')
        markup.add(btn1,btn2)
        markup.add(btn5,btn6)
        markup.add(btn4)
        await bot.send_message(message.chat.id,'Выберите опцию',reply_markup=markup)

async def download_photo(session, photo, index, model_id):
    image_url = await photo.get_url()
    image_path = os.path.join('SearchCar_bot/images', f'{model_id}_photo{index + 1}.jpg')
    print(f"Downloading photo for model_id: {model_id}")
    async with session.get(image_url) as response:
        if response.status == 200:
            with open(image_path, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
            return image_path

async def process_photos(photos_to_process, model_id):
    async with aiohttp.ClientSession() as session:
        print(f'Эта машина под номером {model_id}')
        photo_dict = {}  # Dictionary to store the results with photo index as the key
        tasks = [download_photo(session, photo, index, model_id) for index, photo in enumerate(photos_to_process)]
        for index, task in enumerate(asyncio.as_completed(tasks)):
            downloaded_image = await task
            photo_dict[index] = downloaded_image
        return [photo_dict[i] for i in range(len(photos_to_process))]

async def update_database_with_images(downloaded_images, model_id):
    # Update the database with the paths to the images
    # Replace the following code with your actual database update logic.
    # You may need to use a database library like pymysql or SQLAlchemy.
    update_query = '''UPDATE car_models
                      SET image1 = %s, image2 = %s, image3 = %s, image4 = %s
                      WHERE id = %s'''
    params = (downloaded_images[0], downloaded_images[1], downloaded_images[2], downloaded_images[3], model_id)

    # Execute the update query and commit changes to the database.
    # For this example, we are not using a real database, so we don't execute the query.
    cursor = connection.cursor()
    cursor.execute(update_query, params)
    connection.commit()
    cursor.close()
    


#--------ва-----------------------------------Удалить машину-------------------------------------------------

@dp.callback_query_handler(lambda c: c.data.startswith('delete_model_'))
async def delete_model(query: types.CallbackQuery):
    # Получаем идентификатор модели авто из query.data или из другого источника
    model_id = query.data[13:]  # Предполагается, что идентификатор модели передается в query.data
    print(model_id)
    connection = create_connection()
    try:
        file_list = os.listdir(folder_path)
        cursor = connection.cursor()
        delete_query = '''DELETE FROM car_models WHERE id = %s'''
        params = (model_id,)
        cursor.execute(delete_query, params)
        connection.commit()
        await query.answer("Модель успешно удалена")
        for file_name in file_list:
            if file_name.startswith(f'{model_id}'):
                file_path = os.path.join(folder_path, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Файл {file_name} успешно удален.")
                    else:
                        print(f"{file_name} не является файлом.")
                except Exception as e:
                    print(f"Ошибка при удалении {file_name}: {e}")

    except Error as e:
        await query.answer(f'Ошибка при удалении: {e}')
    finally:
        if connection:
            connection.close()

    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Вывести весь список авто', callback_data='display_cars_admin')
    btn2 = types.InlineKeyboardButton('Назад', callback_data=f'back_admin_1')

    keyboard.add(btn1, btn2)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)

#--------------------------------------Добавить авто-------------------------------------------------




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
            await bot.send_message(message.from_user.id, "Введите цену автомобиля:")
            await AddCarState.next()  # Переход в состояние ожидания цены автомобиля
        except ValueError:
            await bot.send_message(message.from_user.id, "Неверный формат года. Попробуйте еще раз.")






@dp.message_handler(state=AddCarState.price)
async def save_car_data(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_ids:
        await state.update_data(price= message.text)  # Сохраняем значение описания автомобиля
        data = await state.get_data()  # Получаем сохраненные данные из состояния FSM
        mark = data['mark']
        model = data['model']
        year = data['year']
        price = data['price']

        # Вызываем функцию сохранения данных в базу данных
        save_car_to_database(mark, model, year, price)

        await state.finish()
        await bot.send_message(message.from_user.id, "Автомобиль успешно добавлен в базу данных.")
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Вывести весь список авто',callback_data='display_cars_admin')


        keyboard.add(btn1)
        await bot.send_message(message.chat.id,'Выберите опцию',reply_markup=keyboard)

#--------------------------------------Возврат к главному меню админа----------------------------------

@dp.callback_query_handler(lambda c: c.data == 'back_admin_1')
async def go_back_admin_1(query: types.CallbackQuery):
    mark_admin = types.InlineKeyboardMarkup()
    btn_admin_1 = types.InlineKeyboardButton('Мои чаты',callback_data='chats')
    btn_admin_2 = types.InlineKeyboardButton('Управление каталогом',callback_data='change_catalog')
    btn_admin_3 = types.InlineKeyboardButton('Управление FAQ',callback_data='change_faq')
    mark_admin.add(btn_admin_1,btn_admin_2)
    mark_admin.add(btn_admin_3)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=mark_admin)

#---------------------------------Чат с админом--------------------------------------------------------

@dp.callback_query_handler(lambda c: c.data == 'ls')
async def handle_callback_query(query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Чат с админом',url='https://t.me/pavelps92')
    btn2 = types.InlineKeyboardButton('Назад',callback_data='back1')
    keyboard.add(btn1,btn2)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)


#-------------------------------------------Каталог авто для пользователя------------------------------

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


#--------------------------------Марки машин для пользователя ----------------------------------------

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
          
            btn = types.InlineKeyboardButton(f" {car_model[1]} {car_model[2]} {car_model[3]} - {car_model[4]}",callback_data=f'u_models_{car_model[0]}')
            markup.add(btn)
        btn2 = types.InlineKeyboardButton('Назад',callback_data='catalog_auto')
        markup.add(btn2)
    else:
        await bot.send_message(query.message.chat.id,'Нет моделей для данной марки')

    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)

#-------------------------------Просмотр машины пользователем--------------------

@dp.callback_query_handler(lambda c: c.data.startswith('u_models_'))
async def display_model_user(query: types.CallbackQuery):
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
            car_info = f"Марка: {model[1]}\nМодель: {model[2]}\nГод: {model[3]}\nЦена: {model[4]}"
            # Создаем список с медиа-объектами изображений
            media = []
            if model[5]:
                for i in range(5, 9):
                    if model[i]:
                        image_path = model[i]
                        photo = types.InputFile(image_path)
                        media.append(types.InputMediaPhoto(media=photo))
                # Отправляем изображения модели в чат одним сообщением
                await bot.send_media_group(query.message.chat.id, media)


            # Отправляем оставшуюся информацию о модели во втором сообщении
            await bot.send_message(query.message.chat.id, car_info)

            # Отправляем описание модели в чат, если оно есть
            if model[9]:
                description = model[9]
                await bot.send_message(query.message.chat.id, f"Описание: {description}")
        else:
            await bot.send_message(query.message.chat.id, "Модель авто не найдена")

    except Error as e:
        print(f"The error '{e}' occurred")
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Вернуться в каталог',callback_data='catalog_auto')
    btn2 = types.InlineKeyboardButton('Запросить финальную цену', callback_data=f'finish_price_{model_id}')
    keyboard.add(btn1,btn2)
    await bot.send_message(query.message.chat.id,f'Выберите опцию',reply_markup=keyboard)


    

#---------------------------------Запрос финальной цены--------------------------------------------

@dp.callback_query_handler(lambda c: c.data.startswith('finish_price_'))
async def request_final_price(query: types.CallbackQuery):

      # Получаем идентификатор модели авто из query.data или из другого источника
    model_id = query.data[13:]  # Предполагается, что идентификатор модели передается в query.data
    user_id = query.from_user.username
    admin_id = '-908587412'
    user = query.message.chat.id
    # Получаем информацию о модели авто из базы данных
    select_query = '''SELECT * FROM car_models WHERE id = %s'''
    params = (model_id,)
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(select_query, params)
        model = cursor.fetchone()
        car_data = {}
        if model[9]==None:
            car_data = {
            "Марка": model[1],
            "Модель": model[2],
            "Год": model[3],
            "Цена": model[4],


            }
        
        if model[9]!=None:
            car_data = {
            "Марка": model[1],
            "Модель": model[2],
            "Год": model[3],
            "Цена": model[4],
            "Описание": model[5],
            }
            


        if model:
            # Формируем информацию о модели авто
            car_info = f"Марка: {model[1]}\nМодель: {model[2]}\nГод: {model[3]}\nЦена: {model[4]}"
            # Создаем список с медиа-объектами изображений
            media = []
            if model[5]:
                for i in range(5, 9):
                    if model[i]:
                        image_path = model[i]
                        photo = types.InputFile(image_path)
                        media.append(types.InputMediaPhoto(media=photo))
                
    except Error as e:
        print(f"The error '{e}' occurred")
    print(car_data)
    if car_data:
        # Отправляем запрос на финальную цену администратору (здесь замените 'ADMIN_ID' на ID администратора)
        
        message_text = f"Пользователь с username @{user_id} запросил финальную цену для машины:\n\n"
        for key, value in car_data.items():
            message_text += f"{key}: {value}\n"
        await bot.send_message(user, "Ваш запрос на финальную цену отправлен администратору. Ожидайте ответа.")
        await bot.send_message(admin_id, message_text)
        await bot.send_media_group(admin_id, media)

        # Отправляем пользователю подтверждение запроса
        

    else:
        await bot.send_message(user_id, "К сожалению, информация о машине не найдена. Пожалуйста, попробуйте еще раз.")
    
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Вернуться в каталог',callback_data='catalog_auto')
    keyboard.add(btn1)
    await bot.send_message(query.message.chat.id,f'Выберите опцию',reply_markup=keyboard)
#----------------------------------Главное меню для пользователя-------------------------------------

@dp.callback_query_handler(lambda c: c.data == 'back1')
async def go_back_3(query: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Написать в лс',callback_data='ls')
    btn2 = types.InlineKeyboardButton('Каталог авто',callback_data='catalog_auto')
    btn3 = types.InlineKeyboardButton('Ответы на вопросы',callback_data='answers')
    markup.add(btn1,btn2)
    markup.add(btn3)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=markup)


#------------------------------------УПРАВЛЕНИЕ FAQ-----------------------------------------
@dp.callback_query_handler(lambda c: c.data == 'answers')
async def questions_admin(query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Ответ на вопрос 1',callback_data='user_first')
    btn2 = types.InlineKeyboardButton('Ответ на вопрос 2',callback_data='user_second')
    btn3 = types.InlineKeyboardButton('Ответ на вопрос 3',callback_data='user_third')
    btn4 = types.InlineKeyboardButton('Назад',callback_data='back1')
    keyboard.add(btn1)
    keyboard.add(btn2)
    keyboard.add(btn3)
    keyboard.add(btn4)
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)

#-----------------------------------------ВОПРОСЫ---------------------------------------------

@dp.callback_query_handler(lambda c: c.data.startswith('user_'))
async def user_quest(query: types.CallbackQuery):
    qv = query.data[4:]
    qv = 'quest'+qv
    current_answer = get_quest_by_id(qv)
    if current_answer:
        await bot.send_message(query.message.chat.id, f'Текущий ответ на вопрос:\n{current_answer[0][0]}')
    else:
        await bot.send_message(query.message.chat.id, f'Ответ на вопрос  не найден')
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(f'{current_answer}',callback_data='nothing') 
    btn4 = types.InlineKeyboardButton('Назад',callback_data='back1')
    keyboard.add(btn4)
    await bot.send_message(query.message.chat.id, 'Выберите опцию', reply_markup=keyboard)


#-------------------СТАРТ------------------------------------------


if __name__ == '__main__':
    connection = create_connection()  # Создание подключения к базе данных
    create_car_models_table(connection)  # Создание таблицы моделей авто
    create_car_questions(connection)
    executor.start_polling(dp,skip_updates=True)