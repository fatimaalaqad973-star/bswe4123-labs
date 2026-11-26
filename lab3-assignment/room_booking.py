import os
import asyncio
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

app = FastAPI(title="Room Booking Service")

DELAY_SECONDS = float(os.getenv("DELAY_SECONDS", "0.0"))

ROOMS = [
    {"id": "R101", "name": "Lab A", "capacity": 25},
    {"id": "R102", "name": "Hall B", "capacity": 50},
    {"id": "R103", "name": "Auditorium C", "capacity": 120},
]

BOOKINGS = []


class BookingRequest(BaseModel):
    exam_id: str
    room_id: str
    day: str
    start_hour: int
    end_hour: int


@app.middleware("http")
async def add_artificial_delay(request, call_next):
    if DELAY_SECONDS > 0:
        await asyncio.sleep(DELAY_SECONDS)
    return await call_next(request)


@app.get("/rooms")
async def get_rooms():
    return ROOMS


@app.get("/bookings")
async def get_bookings():
    return BOOKINGS


@app.post("/bookings", status_code=201)
async def create_booking(req: BookingRequest, response: Response):
    room = next((r for r in ROOMS if r["id"] == req.room_id), None)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # منع تكرار نفس الامتحان (Idempotency) عند إعادة المحاولة
    existing_exam = next((b for b in BOOKINGS if b["exam_id"] == req.exam_id), None)
    if existing_exam:
        response.status_code = 200
        return existing_exam

    for b in BOOKINGS:
        if b["room_id"] == req.room_id and b["day"].lower() == req.day.lower():
            if req.start_hour < b["end_hour"] and req.end_hour > b["start_hour"]:
                raise HTTPException(status_code=409, detail="Room already booked at this time")

    new_booking = req.model_dump()
    BOOKINGS.append(new_booking)
    return new_booking