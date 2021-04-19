from services import *
import sqlalchemy
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


class Asset(SqlAlchemyBase):
    __tablename__ = 'assets'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    ticker = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_tg = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


class UsersAsset(SqlAlchemyBase):
    __tablename__ = 'list_assets'
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), primary_key=True, nullable=False)
    asset = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('assets.id'), primary_key=True, nullable=False)
    timer = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    kol = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
