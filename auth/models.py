import enum
from db import Base
from sqlalchemy import Column, Integer, String, Enum


class Roles(enum.Enum):
    administrator = 'administrator'
    manager = 'manager'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(Enum(Roles), default=Roles.manager, nullable=False,
                      info={'verbose_name': 'Роль пользователя'})
