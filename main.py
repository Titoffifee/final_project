from functions import *


def start_and_help(update, context):
    insert_user(update.message.from_user.id)
    context.user_data['id_user'] = update.message.from_user.id
    reply_keyboard = [['/menu']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    with open('start_text.txt', 'r', encoding='utf8') as f:
        text = f.read()
        update.message.reply_text(text, reply_markup=markup)


def menu(update, context):
    insert_user(update.message.from_user.id)
    context.user_data['id_user'] = update.message.from_user.id
    keyboard = [[asset, briefcase]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Выберите, что хотите сделать:', reply_markup=markup)
    return 1


def disp(update, context):
    if update.message.text == asset:
        context.user_data['from'] = asset
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
    if context.user_data['from'] == asset:
        return choose_work_asset(update, context)
    else:
        return insert_asset_in_briefcase(update, context)


def choose_asset(update, context):
    if update.message.text == 'список доступных активов':
       return didnt_find_asset(update, context)
    if not check_asset(update.message.text):
        return ERROR(update, context)
    context.user_data['name'] = update.message.text
    if context.user_data['from'] == asset:
        return choose_work_asset(update, context)
    else:
        return insert_asset_in_briefcase(update, context)


def work_with_asset(update, context):
    if update.message.text == 'узнать стоимость актива':
        v = get_cost(update, context)
        if v is None:
            return choose_work_asset(update, context)
        return menu(update, context)
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
    elif update.message.text == 'Добавить актив в портфель':
        update.message.reply_text('Введите название актива:')
        context.user_data['from'] = briefcase
        return 2
    else:
        session = create_session()
        id = session.query(User).filter(User.id_tg == update.message.from_user.id).first().id
        assets_id = session.query(UsersAsset).filter(UsersAsset.user == id).all()
        assets = []
        for i in assets_id:
            assets.append(session.query(Asset).filter(Asset.id == i.asset).first().name)
        keyboard = []
        for i in assets:
            keyboard.append([InlineKeyboardButton(i, callback_data=i)])
        update.message.reply_text('Выберите актив', reply_markup=InlineKeyboardMarkup(keyboard))
        return 10


def insert_asset_in_briefcase(update, context):
    update.message.reply_text('Введите стоимость актива:')
    return 7


def choose_work_all(update, context):
    if update.message.text == 'Очистить портфель':
        id_tg = update.message.from_user.id
        if erase_asset(get_user('id_tg', id_tg).id):
            update.message.reply_text('Портфель очищен')
        else:
            update.message.reply_text('Произошла ошибка')
        return menu(update, context)


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
        elif update.message.text == '6 часов':
            context.user_data['timer'] = 6
        elif update.message.text == '12 часов':
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
    return menu(update, context)


def get_asset_to_work(update, context):
    query = update.callback_query
    variant = query.data
    query.answer()
    query.edit_message_text(text=f"Выбранный актив: {variant}")
    context.user_data['name'] = variant
    context.user_data['id_asset'] = create_session().query(Asset).filter(Asset.name == variant).first().id
    return cycle_briefcase_solo_work(update, context, bot=dp.bot)


def briefcase_solo_work(update, context):
    if update.message.text == 'Узнать стоимость актива':
        v = get_cost(update, context)
        if v is None:
            return cycle_briefcase_solo_work(update, context)
        return menu(update, context)
    elif update.message.text == 'Удалить актив из портфеля':
        if erase_asset(get_user('tg_id', context.user_data['id_user']).id, context.user_data['id_asset']):
            update.message.reply_text('Актив удален')
        else:
            update.message.reply_text('Ошибка во время удаления. Попробуйте ещё раз или воспользуйтесь командой /help')
        return menu(update, context)
    elif update.message.text == 'Изменить данные актива':
        session = create_session()
        asset_db = session.query(UsersAsset).filter(UsersAsset.user == get_user('tg_id', context.user_data['id_user']).id,
                                                 UsersAsset.asset == context.user_data['id_asset']).first()
        message = 'Название: ' + context.user_data['name'] + \
                  '\nКоличество: ' + str(asset_db.kol) + \
                  '\nНачальная стоимость: ' + str(asset_db.cost) + \
                  '\nТаймер: '
        timer = asset_db.timer
        if timer is None:
            timer = 'нет'
        elif timer == 3:
            timer = '3 часа'
        elif timer == 6:
            timer = '6 часов'
        else:
            timer = '12 часов'
        message = message + timer
        update.message.reply_text(message)
        keyboard = ReplyKeyboardMarkup([['Количество', 'Частота оповещений'],
                                        ['Стоимость при покупке']], one_time_keyboard=True)
        update.message.reply_text('Выберите параметр, который хотите поменять:', reply_markup=keyboard)
        return 12


def change_asset(update, context):
    if update.message.text == 'Количество':
        update.message.reply_text('Введите нужное количество')
        return 13
    elif update.message.text == 'Частота оповещений':
        keyboard = ReplyKeyboardMarkup([['3 часа', '6 часов'], ['12 часов', 'без оповещений']],
                                       one_time_keyboard=True)
        update.message.reply_text('Выберите нужную частоту оповещений', reply_markup=keyboard)
        return 14
    else:
        update.message.reply_text('Введите нужную стоимость\nПример: 132.41')
        return 15


def change_kol(update, context):
    try:
        session = create_session()
        new_kol = int(update.message.text)
        asset_db = session.query(UsersAsset).filter(UsersAsset.user == get_user('tg_id', context.user_data['id_user']).id,
                                                 UsersAsset.asset == context.user_data['id_asset']).first()
        asset_db.kol = new_kol
        session.commit()
        update.message.reply_text('Количество изменено')
    except ValueError:
        update.message.reply_text('Данные в неверном формате. Попробуйте снова')
    except Exception:
        update.message.reply_text('Ошибка. Попробуйте ещё раз или воспользуйтесь командой /help')
    return cycle_briefcase_solo_work(update, context)


def change_timer(update, context):
    try:
        new_timer = None
        if update.message.text == '3 часа':
            new_timer = 3
        elif update.message.text == '6 часов':
            new_timer = 6
        elif update.message.text == '12 часов':
            new_timer = 12
        session = create_session()
        asset_db = session.query(UsersAsset).filter(UsersAsset.user == get_user('tg_id', context.user_data['id_user']).id,
                                                 UsersAsset.asset == context.user_data['id_asset']).first()
        asset_db.timer = new_timer
        session.commit()
        update.message.reply_text('Таймер изменен')
    except Exception:
        update.message.reply_text('Ошибка. Попробуйте ещё раз или воспользуйтесь командой /help')
    return cycle_briefcase_solo_work(update, context)


def change_cost(update, context):
    try:
        session = create_session()
        new_cost = float(update.message.text)
        asset_db = session.query(UsersAsset).filter(UsersAsset.user == get_user('tg_id', context.user_data['id_user']).id,
                                                 UsersAsset.asset == context.user_data['id_asset']).first()
        asset_db.cost = new_cost
        session.commit()
        update.message.reply_text('Стоимость при покупке изменена')
    except ValueError:
        update.message.reply_text('Данные в неверном формате. Попробуйте снова')
    except Exception:
        update.message.reply_text('Ошибка. Попробуйте ещё раз или воспользуйтесь командой /help')
    return cycle_briefcase_solo_work(update, context)


if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    menu_command = CommandHandler('menu', menu)
    dp.add_handler(CommandHandler('start', start_and_help))
    conv_handler = ConversationHandler(
        entry_points=[menu_command],
        states={
            1: [MessageHandler(Filters.text([asset, briefcase]), disp)],
            2: [MessageHandler(Filters.text & ~Filters.command, input_asset)],
            3: [MessageHandler(Filters.text & ~Filters.command, choose_asset)],
            4: [MessageHandler(Filters.text(['узнать стоимость актива', 'добавить актив в портфель',
                                             'получить подробную аналитику']), work_with_asset)],
            5: [MessageHandler(Filters.text(['Добавить актив в портфель', 'Поработать с конкретным активом',
                                             'Поработать со всем портфелем']), choose_work_briefcase)],
            6: [MessageHandler(Filters.text(['Очистить портфель']), choose_work_all)],
            7: [MessageHandler(Filters.text & ~Filters.command, insert1)],
            8: [MessageHandler(Filters.text(['3 часа', '6 часов', '12 часов', 'без оповещений']), insert2)],
            9: [MessageHandler(Filters.text & ~Filters.command, insert3)],
            10: [CallbackQueryHandler(get_asset_to_work)],
            11: [MessageHandler(Filters.text(['Изменить данные актива',
                                              'Удалить актив из портфеля',
                                              'Узнать стоимость актива',
                                              'Подробная аналитика']) & ~Filters.command, briefcase_solo_work)],
            12: [MessageHandler(Filters.text(['Количество', 'Частота оповещений', 'Стоимость при покупке'])
                                & ~Filters.command, change_asset)],
            13: [MessageHandler(Filters.text & ~Filters.command, change_kol)],
            14: [MessageHandler(Filters.text & ~Filters.command, change_timer)],
            15: [MessageHandler(Filters.text & ~Filters.command, change_cost)]
        },
        fallbacks=[CommandHandler('help', start_and_help), menu_command]
    )
    dp.add_handler(conv_handler)
    global_init('db/db.sqlite3')
    updater.start_polling()
    updater.idle()
