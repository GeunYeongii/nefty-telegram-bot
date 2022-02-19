import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pycoingecko import CoinGeckoAPI
import os
from assets import assets

# -- Logging -- #
import logging
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console..

coin = CoinGeckoAPI()

APITOKEN = os.environ.get('APITOKEN') 
bot = telebot.TeleBot(APITOKEN)

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("정보 조회하기!", callback_data="true"))
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = bot.send_message(
        message.chat.id, "고래들의 정보를 확인해보세요!", reply_markup=gen_markup())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        jsonfile = assets()
        
        for asset in jsonfile["assets"] :
            ID = asset['id']
            NAME = asset['name']
            LINK = asset['permalink']
            IMAGE = asset['image_preview_url']
            
            # nft 정보를 HTML형식으로 메세지 보내기
            bot.send_message(call.from_user.id, \
                "<b>ID :</b> {}\n \
                <b>Name :</b> {}\n \
                <b>permalink :</b> <a href='{}'>🔗link</a>" \
                .format(ID,NAME,LINK), \
                parse_mode="HTML")
    except:
        bot.send_message(call.from_user.id, "문제가 발생 했습니다. 다시 클릭 해주세요.")
    
bot.polling()



