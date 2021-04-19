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
    update.message.reply_text('Выберите, что хотите сделать:', reply_markup=markup)
    return 1


def disp(update, context):
    if update.message.text == asset:
        update.message.reply_text('Введите название актива, который вы хотите проанализировать')
        return 2
    elif update.message.text == briefcase:
        update.message.reply_text('Что хотите сделать?',
                                  reply_markup=ReplyKeyboardMarkup([['Добавить актив в портфель',
                                                                     'Поработать с конкретным активом'],
                                                                    ['Поработать со всем портфелем']],
                                                                   one_time_keyboard=True))
        return 5
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
        update.message.reply_text('Введите стоимость покупки актива')
        return 7


def choose_work_briefcase(update, context):
    if update.message.text == 'Поработать со всем портфелем':
        update.message.reply_text('Выберите, что хотите сделать:',
                                  reply_markup=ReplyKeyboardMarkup([['Очистить портфель']],
                                                                   one_time_keyboard=True))
        return 6


def choose_work_all(update, context):
    if update.message.text == 'Очистить портфель':
        id_tg = update.message.from_user.id
        if erase_asset(get_user('id_tg', id_tg).id):
            update.message.reply_text('Портфель очищен')
        else:
            update.message.reply_text('Произошла ошибка')
        return END


def insert1(update, context):
    try:
        context.user_data['cost'] = float(update.message.text)
        update.message.reply_text('Выберите частоту оповещений',
                                  reply_markup=ReplyKeyboardMarkup([['3 часа', '6 часов'],
                                                                    ['12 часов', 'без оповещений']],
                                                                   one_time_keyboard=True))
        return 8
    except Exception:
        return ERROR(update, context)


def insert2(update, context):
    try:
        if update.message.text == '3 часа':
            context.user_data['timer'] = 3
        elif update.message.text == '6 часа':
            context.user_data['timer'] = 6
        elif update.message.text == '12 часа':
            context.user_data['timer'] = 12
        else:
            context.user_data['timer'] = None
        update.message.reply_text('Введите количество купленого актива')
        return 9
    except Exception:
        return ERROR(update, context)


def insert3(update, context):
    try:
        context.user_data['kol'] = int(update.message.text)
    except Exception:
        return ERROR(update, context)
    insert_asset(update, context)
    return END


if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    menu_command = CommandHandler('menu', menu)
    dp.add_handler(CommandHandler('start', start_and_help))
    dp.add_handler(CommandHandler('help', start_and_help))
    conv_handler = ConversationHandler(
        entry_points=[menu_command],
        states={
            1: [MessageHandler(Filters.text([asset, briefcase]), disp)],
            2: [MessageHandler(Filters.text, input_asset)],
            3: [MessageHandler(Filters.text, choose_asset)],
            4: [MessageHandler(Filters.text(['узнать стоимость актива', 'добавить актив в портфель',
                                             'получить подробную аналитику']), work_with_asset)],
            5: [MessageHandler(Filters.text(['Добавить актив в портфель', 'Поработать с конкретным активом',
                                             'Поработать со всем портфелем']), choose_work_briefcase)],
            6: [MessageHandler(Filters.text(['Очистить портфель']), choose_work_all)],
            7: [MessageHandler(Filters.text, insert1)],
            8: [MessageHandler(Filters.text(['3 часа', '6 часов', '12 часов', 'без оповещений']), insert2)],
            9: [MessageHandler(Filters.text, insert3)],
        },
        fallbacks=[menu_command]
    )
    dp.add_handler(conv_handler)
    global_init('db/db.sqlite3')
    updater.start_polling()
    updater.idle()
