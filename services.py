from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import requests
from Levenshtein import distance
import datetime as dt


# update.message.from_user.id
# updater.bot.send_message()
# но нужен ID чата = ID пользователя
TOKEN = '1793569905:AAHgC5pxbuqgnH-RICGbbJyC3zsAFcecmm0'
KEY = '8051be96033a3935c4a9cfcb270fccc8'
asset = 'анализ одного актива'
briefcase = 'перейти в портфель'
URL_intraday = 'http://api.marketstack.com/v1/intraday'
URL_eod = 'http://api.marketstack.com/v1/eod'
due3, due6, due12 = 10800, 21600, 43200

my_time = dt.timedelta(hours=3)
month = dt.timedelta(days=30)
month3 = dt.timedelta(days=90)
month6 = dt.timedelta(days=180)
year = dt.timedelta(days=365)

END = ConversationHandler.END


def corr_date(date):
    return date.strftime('%Y-%m-%d')