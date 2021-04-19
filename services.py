from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import requests
from Levenshtein import distance
import datetime as dt


# update.message.from_user.id
# updater.bot.send_message()
# но нужен ID чата = ID пользователя
TOKEN = '1738037077:AAFKcVrhOvPsoT0sU8kZRVvo4rZpoA0gPqo'
KEY = '8051be96033a3935c4a9cfcb270fccc8'
asset = 'анализ одного актива'
briefcase = 'перейти в портфель'
URL_intraday = 'http://api.marketstack.com/v1/intraday'

my_time = dt.timedelta(hours=3)

END = ConversationHandler.END
