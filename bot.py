import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pycoingecko import CoinGeckoAPI
import os

coin = CoinGeckoAPI()

APITOKEN = os.environ.get('APITOKEN') 
bot = telebot.TeleBot(APITOKEN)


currencies = ['Bitcoin', 'Ethereum', 'solana']

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    for i in range(0, 3, 3):
        markup.add(InlineKeyboardButton(currencies[i], callback_data=currencies[i]), InlineKeyboardButton(
            currencies[i+1], callback_data=currencies[i+1]), InlineKeyboardButton(
            currencies[i+2], callback_data=currencies[i+2]))
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = bot.send_message(
        message.chat.id, "코인을 선택해 주세요!", reply_markup=gen_markup())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        x = coin.get_price(ids=call.data, vs_currencies='usd')
        bot.send_message(call.from_user.id, str(x[str(call.data).lower()]['usd'])+" $")
    except:
        bot.send_message(call.from_user.id, "문제가 발생 했습니다. 다시 선택 해주세요.")
bot.polling()
