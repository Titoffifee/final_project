from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup
import requests


# update.message.from_user.id
# updater.bot.send_message()
# но нужен ID чата
TOKEN = '1793569905:AAHgC5pxbuqgnH-RICGbbJyC3zsAFcecmm0'
asset = 'анализ одного актива'
briefcase = 'перейти в портфель'

END = ConversationHandler.END