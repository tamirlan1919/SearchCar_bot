from mysql.connector import Error
from config import TOKEN
from aiogram import Bot,Dispatcher,executor,types
import mysql.connector
from mysql.connector import Error
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
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
                                price VARCHAR(255),
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

def create_car_questions(connection):
    try:
        cursor = connection.cursor()
        create_table_query = '''CREATE TABLE IF NOT EXISTS car_questions (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                quest_first TEXT,
                                quest_second TEXT,
                                quest_third TEXT
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
        select_query = "SELECT id, mark, model,year,price FROM car_models WHERE mark = %s"
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
        select_query = "SELECT id,model,year,price FROM car_models WHERE id = %s"
        cursor.execute(select_query, (id,))
        car_models = cursor.fetchall()
        return car_models
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection:
            connection.close()

# Функция для сохранения автомобиля в базе данных
def save_car_to_database(mark, model, year, price):
    connection = create_connection()
    try:
        cursor = connection.cursor()

        # Подготовка SQL-запроса для вставки данных автомобиля в таблицу
        insert_query = '''INSERT INTO car_models (mark, model, year, price)
                          VALUES (%s, %s, %s, %s)'''
        
        # Параметры для SQL-запроса
        params = (mark, model, year, price)

        # Выполнение SQL-запроса
        cursor.execute(insert_query, params)
        connection.commit()
        
        print('Car added to database successfully')
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection:
            connection.close()
            

def get_all_by_id(idd):
    connection = create_connection()
    try:
        cursor = connection.cursor()
        select_query = "SELECT * FROM car_models WHERE id = %s"
        cursor.execute(select_query, (idd,))
        car_models = cursor.fetchall()
        return car_models
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection:
            connection.close()

def get_quest_by_id(qv):
    connection = create_connection()
    try:
        cursor = connection.cursor()
        # Создаем динамический запрос, подставляя правильное имя поля
        select_query = f"SELECT {qv} FROM car_questions WHERE id = 1"
        cursor.execute(select_query)
        car_quest = cursor.fetchall()
        return car_quest if car_quest else None
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection:
            connection.close()

def update_quest_by_id(qv, new_answer):
    connection = create_connection()
    try:
        cursor = connection.cursor()
        update_query = f"UPDATE car_questions SET {qv} = %s "
        cursor.execute(update_query, (new_answer,))
        connection.commit()
        print(f"Answer for question {qv} with  updated successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection:
            connection.close()