Lab Assignment 2: Campus Room Booking Service

1. Project Description

In this assignment, I developed a Campus Room Booking Service using Python and FastAPI.

The idea of this project is to help students and university staff book rooms for study groups, meetings, and lab sessions.

The system allows users to add rooms, view rooms, create bookings, and delete bookings. It also checks booking times to prevent two people from booking the same room at the same time.

2. Technologies Used

I used the following technologies:

- Python
- FastAPI
- Pydantic
- HTTPX
- Uvicorn

3. API Design

I designed the API with the following operations:

Method| URI| Request Body| Success Code| Error Codes
POST| /rooms| Room information| 201| 409, 422
GET| /rooms| None| 200| None
GET| /rooms/{room_id}| None| 200| 404
PUT| /bookings/{booking_id}| Booking information| 201, 200| 404, 409, 422
GET| /bookings| None| 200| None
GET| /bookings/{booking_id}| None| 200| 404
DELETE| /bookings/{booking_id}| None| 204| 404

4. Data Validation

I used Pydantic models to check the data before accepting it.

The system checks the following:

- Room capacity must be greater than zero.
- Start and end hours must be between 8 and 20.
- The end hour must be greater than the start hour.
- The booking purpose cannot be empty.
- The room must exist before creating a booking.

If the entered data is invalid, the system returns status code 422.

5. Preventing Booking Conflicts

One of the most important parts of this project is preventing overlapping bookings.

Before creating a booking, the system checks if the same room is already booked on the same date.

If the new booking overlaps with an existing booking, the system returns status code 409.

For example:

- First booking: 10:00 to 12:00
- Second booking: 11:00 to 13:00

The second booking is rejected because the times overlap.

But if the second booking starts at 12:00, it is accepted because the first booking ends at that time.

6. Safe Retry Design

I used the PUT method with a booking ID selected by the client.

This helps prevent creating the same booking more than once.

If the client sends the same request again with the same booking ID and the same information, the system returns the existing booking with status code 200.

If the same ID is used with different information, the system returns status code 409.

This makes booking creation safer when a request needs to be sent again.

7. Test Results

The following table shows the test cases and their results.

Test Case| Status Code| Result
Create room| 201| PASS
Get rooms| 200| PASS
Get room| 200| PASS
Unknown room| 404| PASS
Invalid room| 422| PASS
Create booking| 201| PASS
Repeat booking| 200| PASS
Overlapping booking| 409| PASS
Adjacent booking| 201| PASS
Invalid booking| 422| PASS
Unknown booking room| 404| PASS
Get bookings| 200| PASS
Get booking| 200| PASS
Unknown booking| 404| PASS
Delete booking| 204| PASS
Delete unknown booking| 404| PASS

Test Summary

- Total Test Cases: 16
- Passed: 16
- Failed: 0
- Success Rate: 100%

8. How to Run the Project

First, install the required libraries:

pip install fastapi uvicorn pydantic httpx

To start the server, use:

uvicorn main:app --reload

Then open another terminal and run the test file:

python test_bookings.py

9. Conclusion

In this assignment, I learned how to build a REST API using FastAPI.

I also learned how to use Pydantic for data validation, handle HTTP status codes, prevent overlapping bookings, and use PUT requests to avoid duplicate bookings.

The project provides a simple way to manage university rooms and their bookings.