from datetime import date
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator

app = FastAPI(
    title="Campus Room Booking Service",
    description="REST API for university room bookings",
    version="1.0.0"
)

# In-memory storage
rooms = {}
bookings = {}


# -------------------------
# Pydantic Models
# -------------------------

class Room(BaseModel):
    id: str
    building: str
    capacity: int = Field(gt=0)


class Booking(BaseModel):
    room_id: str
    booking_date: date
    start_hour: int = Field(ge=8, le=20)
    end_hour: int = Field(ge=8, le=20)
    purpose: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_hours(self):
        if self.end_hour <= self.start_hour:
            raise ValueError("End hour must be after start hour")
        return self


# -------------------------
# Home
# -------------------------

@app.get("/")
def home():
    return {
        "message": "Campus Room Booking Service is running"
    }


# -------------------------
# Room Operations
# -------------------------

@app.post("/rooms", status_code=201)
def create_room(room: Room):

    if room.id in rooms:
        raise HTTPException(
            status_code=409,
            detail="Room already exists"
        )

    rooms[room.id] = room

    return room


@app.get("/rooms")
def get_rooms():
    return list(rooms.values())


@app.get("/rooms/{room_id}")
def get_room(room_id: str):

    if room_id not in rooms:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    return rooms[room_id]


# -------------------------
# Booking Operations
# -------------------------

@app.put("/bookings/{booking_id}", status_code=201)
def create_booking(booking_id: str, booking: Booking):

    # Check if room exists
    if booking.room_id not in rooms:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    # Make repeated requests safe
    if booking_id in bookings:

        if bookings[booking_id] == booking:
            return JSONResponse(
                status_code=200,
                content=booking.model_dump(mode="json")
            )

        raise HTTPException(
            status_code=409,
            detail="Booking ID already exists with different data"
        )

    # Check overlapping bookings
    for existing in bookings.values():

        if (
            existing.room_id == booking.room_id
            and existing.booking_date == booking.booking_date
            and booking.start_hour < existing.end_hour
            and existing.start_hour < booking.end_hour
        ):
            raise HTTPException(
                status_code=409,
                detail="Room is already booked during this time"
            )

    bookings[booking_id] = booking

    return booking


@app.get("/bookings")
def get_bookings():
    return list(bookings.values())


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str):

    if booking_id not in bookings:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return bookings[booking_id]


@app.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: str):

    if booking_id not in bookings:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    del bookings[booking_id]

    return Response(status_code=204)