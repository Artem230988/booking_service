import datetime
from typing import List

from pydantic import BaseModel


class RoomSchema(BaseModel):
    room_number: int
    price: int
    seat_count: int

    class Config:
        orm_mode = True


class RoomOutSchema(RoomSchema):
    id: int


class BookingSchema(BaseModel):
    date_from: datetime.date
    date_to: datetime.date

    class Config:
        orm_mode = True


class BookingInSchema(BookingSchema):
    room_number: int


class BookingOutSchema(BookingSchema):
    room_number: int
    id: int


class RoomInfoSchema(RoomSchema):
    bookings: List[BookingSchema]
