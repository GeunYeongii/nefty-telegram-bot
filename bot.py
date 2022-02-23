import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pycoingecko import CoinGeckoAPI
import os
from WhaleTracker.nftgo import nftgoAPI

# -- Whale Tracker -- #
nft = nftgoAPI()
nft.get_bought_list()

# -- Logging -- #
import logging
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console..

APITOKEN = '5101309356:AAHowCuy5dMrisjkGivPXionz4-xBzalXSs'
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
        names = nft.get_name_list()
        prices = nft.get_price_list('KRW','ETH')
        changes = nft.get_change_list()
        buyers = nft.get_buyer_list()
        images = nft.get_nft_image()
        
        for name,price,change,buyer,image in zip(names,prices,changes,buyers,images) :
             
            # nft 정보를 HTML형식으로 메세지 보내기
            bot.send_message(call.from_user.id,"<b>이름 :</b> {0}\n<b>{1} :</b> {2}\n<b>{3} : </b> {4}원\n<b>변동률 :</b> {5}%\n<b>구매자 :</b> <a href='https://opensea.io/{6}'>🔗Opensea Link</a>\n<b>NFT :</b> <a href='{7}'> ▶ 이미지 보러가기</a>".format(name,price['ETH'][1],price['ETH'][0],price['KRW'][1],format(price['KRW'][0],','),change['percent'],buyer,image),parse_mode="HTML")
    except:
        bot.send_message(call.from_user.id, "문제가 발생 했습니다. 다시 클릭 해주세요.")
    
bot.polling()








