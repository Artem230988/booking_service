from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, exists
import datetime

import models, schemas
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_


async def get_rooms(session: AsyncSession):
    result = await session.execute(select(models.Room))
    rooms = result.scalars().all()
    return rooms


async def create_room(room: schemas.RoomSchema, session: AsyncSession):
    db_room = models.Room(**room.dict())
    session.add(db_room)
    await session.commit()
    await session.refresh(db_room)
    return db_room


async def get_room_by_room_number(room_number: int, session: AsyncSession):
    query = select(models.Room).where(models.Room.room_number == room_number)
    result = await session.execute(query)
    return result.scalars().first()


async def get_free_rooms(date_from, date_to, seat_count, session: AsyncSession):
    query = select(models.Room).distinct(models.Room.id).join(models.Booking).\
        where(models.Room.seat_count.in_(seat_count)).\
        filter(or_(date_from >= models.Booking.date_to, date_to <= models.Booking.date_from))
    result = await session.execute(query)
    rooms = result.scalars().all()
    return rooms


async def room_booking_exists(date_from, date_to, room_id, session: AsyncSession):
    query = select(models.Booking).join(models.Room).\
        where(models.Room.id == room_id).\
        filter(or_(and_(date_from >= models.Booking.date_from, date_from < models.Booking.date_to),\
                   and_(date_to > models.Booking.date_from, date_to < models.Booking.date_to),\
                   and_(date_from <= models.Booking.date_from, date_to >= models.Booking.date_to)))
    query = exists(query).select()
    result = await session.execute(query)
    booking_exists = result.scalars().first()
    return booking_exists


async def create_booking(booking: schemas.BookingInSchema, session: AsyncSession):
    room = await get_room_by_room_number(booking.room_number, session)
    if not room:
        raise HTTPException(status_code=400, detail="This room_number don't registered")
    booking_exists = await room_booking_exists(booking.date_from, booking.date_to, room.id, session)
    if booking_exists:
        raise HTTPException(status_code=400, detail="This number is busy on these dates")
    db_booking = models.Booking(
        date_from=booking.date_from,
        date_to=booking.date_to,
        room_id=room.id
    )
    session.add(db_booking)
    await session.commit()
    await session.refresh(db_booking)
    booking = schemas.BookingOutSchema(
        date_from=db_booking.date_from,
        date_to=db_booking.date_to,
        room_number=room.room_number,
        id=db_booking.id
    )
    return booking


async def get_booking(pk: int, session: AsyncSession):
    query = select(models.Booking).where(models.Booking.id == pk)
    result = await session.execute(query)
    return result.scalars().first()


async def destroy_booking(pk: int, session: AsyncSession):
    booking = await get_booking(pk, session)
    delta = booking.date_from - datetime.date.today()
    if delta.days < 3:
        raise HTTPException(
            status_code=400,
            detail="Reservations cannot be canceled less than three days "
                   "before the date of arrival ")
    await session.execute(
        delete(models.Booking).where(models.Booking.id == pk))
    await session.commit()


async def get_room_info(room_number: int, session: AsyncSession):
    query = select(models.Room).options(selectinload(models.Room.bookings)).where(models.Room.room_number == room_number)
    result = await session.execute(query)
    if not result:
        raise HTTPException(status_code=400, detail="This room_number don't registered")
    room = result.scalars().first()
    return room
