import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db import init_db, get_session

import schemas, crud
from auth.auth import router as auth_router
from auth.service import get_current_user
from auth.schemas import BaseUser


app = FastAPI()
app.include_router(auth_router)


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/rooms", response_model=List[schemas.RoomOutSchema])
async def get_all_rooms(session: AsyncSession = Depends(get_session),
                        user: BaseUser = Depends(get_current_user)):
    rooms = await crud.get_rooms(session)
    return rooms


@app.post("/rooms", response_model=schemas.RoomOutSchema)
async def create_room(room: schemas.RoomSchema,
                      session: AsyncSession = Depends(get_session),
                      user: BaseUser = Depends(get_current_user)):
    db_room = await crud.get_room_by_room_number(room.room_number, session)
    if db_room:
        raise HTTPException(status_code=400, detail="This room_number already registered")
    return await crud.create_room(room, session)


@app.get("/free_rooms", response_model=List[schemas.BookingOutSchema])
async def get_free_rooms(
        day_from: datetime.date,
        day_to: datetime.date,
        seat_count: List[int] = Query([]),
        session: AsyncSession = Depends(get_session),
        user: BaseUser = Depends(get_current_user)):
    rooms = await crud.get_free_rooms(day_from, day_to, seat_count, session)
    return rooms


@app.post("/bookings", response_model=schemas.BookingOutSchema)
async def create_booking(booking: schemas.BookingInSchema,
                         session: AsyncSession = Depends(get_session),
                         user: BaseUser = Depends(get_current_user)):
    return await crud.create_booking(booking, session)


@app.get("/bookings/{pk}", response_model=schemas.BookingSchema)
async def get_booking_by_id(pk: int,
                            session: AsyncSession = Depends(get_session),
                            user: BaseUser = Depends(get_current_user)):
    booking = await crud.get_booking(pk, session)
    return booking


@app.delete("/bookings/{pk}")
async def destroy_booking_by_id(pk: int,
                                session: AsyncSession = Depends(get_session),
                                user: BaseUser = Depends(get_current_user)):
    await crud.destroy_booking(pk, session)


@app.get("/rooms_info/{room_number}", response_model=schemas.RoomInfoSchema)
async def get_room_info(room_number: int,
                        session: AsyncSession = Depends(get_session),
                        user: BaseUser = Depends(get_current_user)):
    return await crud.get_room_info(room_number, session)
