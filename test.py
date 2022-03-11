
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from WhaleTracker.nftgo import nftgoAPI
import requests

# -- Whale Tracker -- #
nft = nftgoAPI()
nft.get_bought_list()

# -- Logging -- #
import logging
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console..


APITOKEN = 'API-KEY'
bot = telebot.TeleBot(APITOKEN)

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("지갑 추적", callback_data="wallet"),
               InlineKeyboardButton("FP 알림 설정", callback_data="fp"),
               InlineKeyboardButton("고래 거래 기록", callback_data="whales"))
    return markup

def assets(owner) :
    params = {
        "owner" : owner,
        "limit" : 5,
        "offset" : 0
    }
    return requests.get("https://testnets-api.opensea.io/api/v1/assets", params=params).json()


def wallet_handler(message) :
    address = message.text
    data = assets(address)
    print(data)
    bot.send_message(message.from_user.id, "- data section -")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = bot.send_message(
        message.chat.id, "고래들의 정보를 확인해보세요!", reply_markup=gen_markup())



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if(call.data=='whales') :
            names = nft.get_name_list()
            prices = nft.get_price_list('KRW','ETH')
            changes = nft.get_change_list()
            buyers = nft.get_buyer_list()
            images = nft.get_nft_image()
            times = nft.get_nft_time()
            for name,price,change,buyer,image,time in zip(names,prices,changes,buyers,images,times) :            
                # nft 정보를 HTML형식으로 메세지 보내기
                bot.send_message(call.from_user.id,"<b>이름 :</b> {0}({8} 전)\n<b>{1} :</b> {2}\n<b>{3} : </b> {4}원\n<b>가격 변동률 :</b> {5}%\n<b>구매자 :</b> <a href='https://opensea.io/{6}'>🔗Opensea Link</a>\n<b>NFT :</b> <a href='{7}'> ▶ 이미지 보러가기</a>\n<b>Time :</b> {8} 전".format(name,price['ETH'][1],price['ETH'][0],price['KRW'][1],format(price['KRW'][0],','),change['percent'],buyer,image,time),parse_mode="HTML")
        elif(call.data=='wallet') :
            sent_msg = bot.send_message(call.from_user.id, "주소를 입력해주세요!")
            bot.register_next_step_handler(sent_msg, wallet_handler)
    except:
        bot.send_message(call.from_user.id, "문제가 발생 했습니다. 다시 클릭 해주세요.")
    # https://nftgo.io/api/v1/whales-activity-by-addr?addr=0x0667640ab57cb909b343157d718651ea49141a75&cid=all&action=buy&to=1646578799999&scroll=0&limit=15&isListed=1
bot.polling()








