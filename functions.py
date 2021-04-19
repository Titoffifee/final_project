from sql import *


def didnt_find_asset(update, context):
    update.message.reply_text('ПРИКРЕПИ ФАЙЛ\nДля продолжения работы вернитесь в меню')
    return END


def insert_user(my_id):
    session = create_session()
    if len(session.query(User).filter(User.id_tg == my_id).all()) == 0:
        new_user = User()
        new_user.id_tg = my_id
        session.add(new_user)
        session.commit()


def check_asset(name_asset):
    session = create_session()
    if len(session.query(Asset).filter(Asset.name == name_asset).all()) == 0:
        return False
    return True


def get_asset(key, n):
    session = create_session()
    if key == 'id':
        try:
            return session.query(Asset).filter(Asset.id == n).first()
        except Exception:
            return None
    else:
        try:
            return session.query(Asset).filter(Asset.name == n).first()
        except Exception:
            return None


def get_user(key, n):
    session = create_session()
    try:
        if key == 'id':
            return session.query(User).filter(User.id == n).first()
        else:
            return session.query(User).filter(User.id_tg == n).first()
    except Exception:
        return None


def get_best(s):
    session = create_session()
    names = [el.name for el in session.query(Asset).all()]
    ans = []
    for i in names:
        if len(ans) > 10:
            break
        if s.lower() in i.lower():
            ans.append(i)
    for i in sorted(names, key=lambda x: distance(x.lower(), s.lower())):
        if len(ans) > 10:
            break
        if i not in ans:
            ans.append(i)
    return list(map(lambda x: [x], ans[:21]))


def ERROR(update, context):
    update.message.reply_text('Ответ такого формата не предполагается. '
                              'Для продолжения работы воспользуйтесь командой /menu')
    return END


def choose_work_asset(update, context):
    keyboard = [['узнать стоимость актива', 'добавить актив в портфель'], ['получить подробную аналитику']]
    update.message.reply_text('Выберите необходимое действие:',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return 4


def get_time(update, context):
    return my_time


def erase_asset(id_user=-1, id_asset=-1):
    print(id_user, id_asset)
    session = create_session()
    try:
        for el in session.query(UsersAsset).all():
            if el.user == id_user:
                if id_asset == -1 or el.asset == id_asset:
                    session.delete(el)
        session.commit()
        return True
    except Exception:
        return False


def insert_asset(update, context):
    try:
        new_asset = UsersAsset()
        new_asset.user = get_user('id_tg', update.message.from_user.id).id
        new_asset.asset = get_asset('name', context.user_data['name']).id
        new_asset.kol = context.user_data['kol']
        new_asset.cost = context.user_data['cost']
        new_asset.timer = context.user_data['timer']
        session = create_session()
        session.add(new_asset)
        session.commit()
        update.message.reply_text('Актив успешно добавлен')
    except Exception as e:
        print(e)
        update.message.reply_text('Произошла ошибка во время добавления')


def get_cost(update, context):
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
        message = 'открытие: ' + str(last_change['open']) + \
                  '\nзакрытие: ' + str(last_change['close']) + \
                  '\nЦеновой максимум: ' + str(last_change['high']) + \
                  '\nЦеновой минимум: ' + str(last_change['low']) + \
                  '\nДата получения данных: ' + date.strftime('%d.%m.%Y %H:%M:%S')
        update.message.reply_text(message)
    except Exception:
        update.message.reply_text('Произошла ошибка во время получения данных.')
        return 1


def cycle_briefcase_solo_work(update, context, bot=None):
    keyboard = ReplyKeyboardMarkup([['Изменить данные актива', 'Удалить актив из портфеля'],
                                    ['Узнать стоимость актива', 'Подробная аналитика']])
    if bot is None:
        update.message.reply_text('Выберите, что хотите сделать', reply_markup=keyboard)
    else:
        bot.send_message(text='Выберите, что хотите сделать',
                         reply_markup=keyboard,
                         chat_id=context.user_data['id_user'])
    return 11