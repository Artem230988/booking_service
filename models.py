from sqlalchemy import Column, ForeignKey, Integer, Date, Text, Enum
from sqlalchemy.orm import relationship

from db import Base


class Booking(Base):
    __tablename__ = 'booking'

    id = Column(Integer, primary_key=True, index=True)
    date_from = Column(Date, nullable=False, info={'verbose_name': 'Дата заезда'})
    date_to = Column(Date, nullable=False, info={'verbose_name': 'Дата выезда'})
    room_id = Column(
        Integer,
        ForeignKey('room.id', ondelete='CASCADE'),
        nullable=False
    )
    room = relationship("Room", back_populates="bookings")


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(Integer, unique=True, nullable=False, info={'verbose_name': 'Номер комнаты'})
    price = Column(Integer, nullable=False, info={'verbose_name': 'Цена за сутки'})
    seat_count = Column(Integer, nullable=False, info={'verbose_name': 'Кол-во мест'})
    bookings = relationship("Booking", back_populates="room")
