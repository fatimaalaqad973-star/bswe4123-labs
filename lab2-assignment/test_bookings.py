import httpx

BASE_URL = "http://127.0.0.1:8000"

client = httpx.Client(base_url=BASE_URL)


def test(name, response, expected):
    result = "PASS" if response.status_code == expected else "FAIL"
    print(f"{name}: {response.status_code} | Expected: {expected} | {result}")


# Create room
test("Create room", client.post("/rooms", json={
    "id": "B205",
    "building": "Engineering",
    "capacity": 30
}), 201)

# Get rooms
test("Get rooms", client.get("/rooms"), 200)

# Get room
test("Get room", client.get("/rooms/B205"), 200)

# Unknown room
test("Unknown room", client.get("/rooms/B999"), 404)

# Invalid room
test("Invalid room", client.post("/rooms", json={
    "id": "B300",
    "building": "Science",
    "capacity": -5
}), 422)

booking = {
    "room_id": "B205",
    "booking_date": "2026-12-01",
    "start_hour": 10,
    "end_hour": 12,
    "purpose": "Study group"
}

# Create booking
test("Create booking", client.put("/bookings/BOOK001", json=booking), 201)

# Repeat booking
test("Repeat booking", client.put("/bookings/BOOK001", json=booking), 200)

# Overlapping booking
test("Overlapping booking", client.put("/bookings/BOOK002", json={
    **booking, "start_hour": 11, "end_hour": 13
}), 409)

# Adjacent booking
test("Adjacent booking", client.put("/bookings/BOOK003", json={
    **booking, "start_hour": 12, "end_hour": 13
}), 201)

# Invalid booking
test("Invalid booking", client.put("/bookings/BOOK004", json={
    **booking, "start_hour": 14, "end_hour": 10
}), 422)

# Unknown room in booking
test("Unknown booking room", client.put("/bookings/BOOK005", json={
    **booking, "room_id": "B999"
}), 404)

# Get bookings
test("Get bookings", client.get("/bookings"), 200)

# Get booking
test("Get booking", client.get("/bookings/BOOK001"), 200)

# Unknown booking
test("Unknown booking", client.get("/bookings/BOOK999"), 404)

# Delete booking
test("Delete booking", client.delete("/bookings/BOOK001"), 204)

# Delete unknown booking
test("Delete unknown booking", client.delete("/bookings/BOOK999"), 404)

client.close()