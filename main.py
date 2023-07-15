from config import TOKEN
from aiogram import Bot,Dispatcher,executor,types

bot = Bot(TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message:types.Message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Написать в лс',callback_data='ls')
    btn2 = types.InlineKeyboardButton('Каталог авто',callback_data='catalog_auto')
    btn3 = types.InlineKeyboardButton('Ответы на вопросы',callback_data='answers')
    markup.add(btn1,btn2)
    markup.add(btn3)
    await bot.send_message(message.chat.id,'Привет',reply_markup=markup)

@dp.callback_query_handler()
async def handle_callback_query(query: types.CallbackQuery):
    if query.data == 'ls':
        await query.answer('Напиши ваше сообщение ниже')

executor.start_polling(dp)
