from config import TOKEN
from aiogram import Bot,Dispatcher,executor,types
import mysql.connector
from mysql.connector import Error
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# Определение состояний FSM

class AddCarState(StatesGroup):
    mark = State()
    model = State()
    year = State()
    price = State()
    image1 = State()
    image2 = State()
    image3 = State()
    image4 = State()
    description = State()