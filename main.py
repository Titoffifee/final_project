from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup
import requests


# update.message.from_user.id
TOKEN = '1793569905:AAHgC5pxbuqgnH-RICGbbJyC3zsAFcecmm0'


def start_and_help(update, context):
    reply_keyboard = [['/menu']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = 'Добро пожаловать в инвестиционного помощника!\n' \
           'данный бот позволяет вам получать котировки активов через временные интервалы или по необходимости.\n' \
           'С каждым запросом, кроме текущей стоимости, приходит также дополнительна аналитика.'
    update.message.reply_text(text, reply_markup=markup)


if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start_and_help))
    dp.add_handler(CommandHandler('help', start_and_help))
    updater.start_polling()
    updater.idle()