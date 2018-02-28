import telebot
token = '426758191:AAH77L8fIWpCgc68tJ_WzWmBm-lgXsTiIpw'
print('Bot started with token: {}'.format(token))

bot = telebot.TeleBot(token= token, threaded=False)