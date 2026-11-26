import asyncio
import logging
import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("exam_scheduler")

app = FastAPI(title="Exam Scheduler Service")

ROOM_SERVICE_URL = os.getenv("ROOM_SERVICE_URL", "http://127.0.0.1:8001")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "2.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))


class ExamRequest(BaseModel):
    id: str
    course_code: str
    day: str
    start_hour: int
    end_hour: int
    students: int


@app.get("/config")
async def get_config():
    return {
        "room_service_url": ROOM_SERVICE_URL,
        "timeout_seconds": REQUEST_TIMEOUT,
        "max_retries": MAX_RETRIES,
    }


async def call_with_retry(client: httpx.AsyncClient, method: str, url: str, **kwargs):
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = await client.request(method, url, **kwargs)

            if response.status_code in (404, 409):
                return response

            if response.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"Server returned {response.status_code}",
                    request=response.request,
                    response=response,
                )

            return response

        except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError) as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                backoff_seconds = 0.5 * (2**attempt)
                logger.warning(
                    "Attempt %d/%d failed for %s %s (%s). Retrying in %.1fs...",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    method,
                    url,
                    exc,
                    backoff_seconds,
                )
                await asyncio.sleep(backoff_seconds)
            else:
                logger.error(
                    "All %d attempts failed for %s %s: %s",
                    MAX_RETRIES + 1,
                    method,
                    url,
                    exc,
                )

    raise HTTPException(
        status_code=503,
        detail=f"Room Booking Service unreachable after {MAX_RETRIES} retries: {last_error}",
    )


def has_time_overlap(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    return start_a < end_b and end_a > start_b


@app.post("/exams", status_code=201)
async def create_exam(exam: ExamRequest):
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        rooms_resp = await call_with_retry(client, "GET", f"{ROOM_SERVICE_URL}/rooms")
        if rooms_resp.status_code != 200:
            raise HTTPException(status_code=503, detail="Failed to retrieve rooms")
        rooms = rooms_resp.json()

        bookings_resp = await call_with_retry(client, "GET", f"{ROOM_SERVICE_URL}/bookings")
        if bookings_resp.status_code != 200:
            raise HTTPException(status_code=503, detail="Failed to retrieve bookings")
        bookings = bookings_resp.json()

        existing_booking = next((b for b in bookings if b["exam_id"] == exam.id), None)
        if existing_booking:
            booked_room = next(
                (r for r in rooms if r["id"] == existing_booking["room_id"]), None
            )
            return {
                "exam_id": exam.id,
                "course_code": exam.course_code,
                "booked_room": booked_room,
                "booking": existing_booking,
            }

        candidate_rooms = sorted(
            [r for r in rooms if r["capacity"] >= exam.students],
            key=lambda r: r["capacity"],
        )

        for room in candidate_rooms:
            is_occupied = any(
                b["room_id"] == room["id"]
                and b["day"].lower() == exam.day.lower()
                and has_time_overlap(
                    exam.start_hour, exam.end_hour, b["start_hour"], b["end_hour"]
                )
                for b in bookings
            )
            if is_occupied:
                continue

            booking_data = {
                "exam_id": exam.id,
                "room_id": room["id"],
                "day": exam.day,
                "start_hour": exam.start_hour,
                "end_hour": exam.end_hour,
            }
            book_resp = await call_with_retry(
                client, "POST", f"{ROOM_SERVICE_URL}/bookings", json=booking_data
            )

            if book_resp.status_code in (200, 201):
                return {
                    "exam_id": exam.id,
                    "course_code": exam.course_code,
                    "booked_room": room,
                    "booking": book_resp.json(),
                }

            if book_resp.status_code in (404, 409):
                continue

        raise HTTPException(
            status_code=409,
            detail="No free room large enough is available for this exam",
        )