from services import *


def start_and_help(update, context):
    reply_keyboard = [['/menu']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    with open('start_text.txt', 'r', encoding='utf8') as f:
        text = f.read()
        update.message.reply_text(text, reply_markup=markup)


def menu(update, context):
    keyboard = [[asset, briefcase]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Выберите что хотите сделать:', reply_markup=markup)
    return 1


def disp(update, context):
    if update.message.text == asset:
        update.message.reply_text('Введите название актива, который вы хотите проанализировать')
        return 2
    elif update.message.text == briefcase:
        return 666
    else:
        update.message.reply_text('Такой ответ не предполагается. Возвращение в меню')
        return END


def input_asset(update, context):
    update.message.reply_text('юху')
    on_base = []
    if not on_base:
        return 404
    context.user_data['ticket'] = update.message.text
    return 3


if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    menu_command = CommandHandler('menu', menu)
    dp.add_handler(CommandHandler('start', start_and_help))
    dp.add_handler(CommandHandler('help', start_and_help))
    conv_handler = ConversationHandler(
        entry_points=[menu_command],
        states={
            1: [MessageHandler(Filters.text, disp)],
            2: [MessageHandler(Filters.text, input_asset)],
            404: ['Вывод списка доступных']
        },
        fallbacks=[menu_command]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()