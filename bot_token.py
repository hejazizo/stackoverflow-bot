import telebot
token = ''
print('Bot started with token: {}'.format(token))

bot = telebot.TeleBot(token= token, threaded=False)
