from sql import *


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
    return list(map(lambda x: [x], ans[:11]))


def ERROR(update, context):
    update.message.reply_text('Ответ такого формата не предполагается. '
                              'Для продолжения работы воспользуйтесь командой /menu')
    return END


def choose_work_asset(update, context):
    keyboard = [['узнать стоимость актива', 'добавить актив в портфель'], ['получить подробную аналитику']]
    update.message.reply_text('Выберите необходимое действие:',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return 4
