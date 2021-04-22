from sql import *


def didnt_find_asset(update, context):
    context.bot.send_document(update.message.from_user.id, open('assets.txt', 'rb'))


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
    from main import menu
    return menu(update, context)


def choose_work_asset(update, context):
    keyboard = [['узнать стоимость актива', 'добавить актив в портфель'], ['получить подробную аналитику']]
    update.message.reply_text('Выберите необходимое действие:',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return 4


def erase_asset(id_user=-1, id_asset=-1):
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
        if len(session.query(UsersAsset).filter(UsersAsset.user == new_asset.user, UsersAsset.asset == new_asset.asset).all()) != 0:
            update.message.reply_text('Данный актив уже есть в вашем портфеле')
            return None
        session.add(new_asset)
        session.commit()
        update.message.reply_text('Актив успешно добавлен')
    except Exception as e:
        update.message.reply_text('Произошла ошибка во время добавления')


def get_ticker(name):
    ticker = get_asset('name', name).ticker
    return ticker


def get_cost(ticker):
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
            date = date + (my_time -
                           dt.timedelta(hours=int(last_change['date'].split('+')[1][:2]),
                                        minutes=int(last_change['date'].split('+')[1][2:])))
        else:
            date = date + (my_time +
                           dt.timedelta(hours=int(last_change['date'].split('-')[1][:2]),
                                        minutes=int(last_change['date'].split('-')[1][2:])))

        message = 'открытие: ' + str(last_change['open']) + \
                  '\nзакрытие: ' + str(last_change['close']) + \
                  '\nЦеновой максимум: ' + str(last_change['high']) + \
                  '\nЦеновой минимум: ' + str(last_change['low']) + \
                  '\nДата получения данных: ' + date.strftime('%d.%m.%Y %H:%M:%S')
        cost = (last_change['high'] + last_change['low']) / 2
        return (message, cost)
    except Exception as e:
        return (1, 'Произошла ошибка во время получения данных.')


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


def get_analys(ticker):
    month_before, year_before = dt.datetime.now() - month, dt.datetime.now() - year
    month3_before, month6_before = dt.datetime.now() - month3, dt.datetime.now() - month6
    params1, params2 = {'access_key': KEY, 'symbols': ticker, 'date_to': corr_date(month_before)},\
                       {'access_key': KEY, 'symbols': ticker, 'date_to': corr_date(year_before)}
    params3, params4 = {'access_key': KEY, 'symbols': ticker, 'date_to': corr_date(month3_before)}, \
                       {'access_key': KEY, 'symbols': ticker, 'date_to': corr_date(month6_before)}
    params = {'access_key': KEY, 'symbols': ticker}
    try:
        ans1, ans2 = requests.get(URL_eod, params=params1), requests.get(URL_eod, params=params2)
        ans3, ans4 = requests.get(URL_eod, params=params3), requests.get(URL_eod, params=params4)
        now = requests.get(URL_eod, params=params)
        m, y = ans1.json()['data'][0], ans2.json()['data'][0]
        m3, m6 = ans3.json()['data'][0], ans4.json()['data'][0]
        n = now.json()['data'][0]
        cost_now, cost_m, cost_y = (n['high'] + n['low']) / 2, \
                                   (m['high'] + m['low']) / 2, \
                                   (y['high'] + y['low']) / 2
        cost_m3, cost_m6 = (m3['high'] + m3['low']) / 2,\
                           (m6['high'] + m6['low']) / 2
        message = []
        message.append('Текущая цена: ' + str(cost_now))
        message.append('Рост за месяц: ' + str((cost_now - cost_m) / cost_m * 100) +
                       '% (' + str(cost_m) + ' -> ' + str(cost_now) + ')')
        message.append('Рост за 3 месяца: ' + str((cost_now - cost_m3) / cost_m3 * 100) +
                       '% (' + str(cost_m3) + ' -> ' + str(cost_now) + ')')
        message.append('Рост за 6 месяцев: ' + str((cost_now - cost_m6) / cost_m6 * 100) +
                       '% (' + str(cost_m6) + ' -> ' + str(cost_now) + ')')
        message.append('Рост за год :' + str((cost_now - cost_y) / cost_y * 100) +
                       '% (' + str(cost_y) + ' -> ' + str(cost_now) + ')')
        return '\n'.join(message)
    except Exception as e:
        return (1, 'Произошла ошибка во время получения данных.')