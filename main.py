from functions import *


def start_and_help(update, context):
    insert_user(update.message.from_user.id)
    reply_keyboard = [['/menu']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    with open('start_text.txt', 'r', encoding='utf8') as f:
        text = f.read()
        update.message.reply_text(text, reply_markup=markup)


def menu(update, context):
    insert_user(update.message.from_user.id)
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
        return ERROR(update, context)


def input_asset(update, context):
    if not check_asset(update.message.text):
        keyboard = get_best(update.message.text) + [['список доступных активов']]
        update.message.reply_text('Прямого совпадения не найдено. '
                                  'Выберите нужную акцию пользуясь клавиатурой, '
                                  'вернитесь в меню или ознакомьтесь со списком доступынх активов',
                                  reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return 3
    context.user_data['name'] = update.message.text
    return choose_work_asset(update, context)


def choose_asset(update, context):
    if update.message.text == 'список доступных активов':
       return didnt_find_asset(update, context)
    if not check_asset(update.message.text):
        return ERROR(update, context)
    context.user_data['name'] = update.message.text
    return choose_work_asset(update, context)


def work_with_asset(update, context):
    if update.message.text == 'узнать стоимость актива':
        ticker = get_asset('name', context.user_data['name']).ticker
        params = {
            'access_key': KEY,
            'symbols': ticker,
        }
        ans = requests.get(URL_intraday, params=params)
        try:
            last_change = ans.json()['data'][0]
            date = last_change['date'].split('T')[0].split('-')
            time = last_change['date'].split('T')[1].split(':')
            time[-1] = time[-1][:2]
            date = dt.datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]),
                               hour=int(time[0]), minute=int(time[1]), second=int(time[2]))
            if '+' in last_change['date']:
                date = date + (get_time(update, context) -
                               dt.timedelta(hours=int(last_change['date'].split('+')[1][:2]),
                                            minutes=int(last_change['date'].split('+')[1][2:])))
            else:
                date = date + (get_time(update, context) +
                               dt.timedelta(hours=int(last_change['date'].split('-')[1][:2]),
                                            minutes=int(last_change['date'].split('-')[1][2:])))
            message = 'открытие: ' + str(last_change['open']) +\
                      '\nзакрытие: ' + str(last_change['close']) +\
                      '\nЦеновой максимум: ' + str(last_change['high']) +\
                      '\nЦеновой минимум: ' + str(last_change['low']) +\
                      '\nДата получения данных: ' + date.strftime('%d.%m.%Y %H:%M:%S')
            update.message.reply_text(message)
            return choose_work_asset(update, message)
        except Exception:
            update.message.reply_text('Произошла ошибка во время получения данных. '
                                      'Для возвращения в меню воспользуйтесь командой /menu')
            return END

    elif update.message.text == 'получить подробную аналитику':
        pass
    else:
        pass


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
            3: [MessageHandler(Filters.text, choose_asset)],
            4: [MessageHandler(Filters.text, work_with_asset)],
        },
        fallbacks=[menu_command]
    )
    dp.add_handler(conv_handler)
    global_init('db/db.sqlite3')
    updater.start_polling()
    updater.idle()