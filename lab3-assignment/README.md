Lab Assignment 3: The Exam Scheduler Service

1. Introduction

In this lab, I worked on building an Exam Scheduler Service that helps automate the process of booking rooms for exams.

The main idea is to make the booking process easier by connecting the Exam Scheduler Service with the Room Booking Service. The scheduler receives exam information, checks the available rooms, and selects the smallest room that has enough capacity for the students and is free at the requested time.

2. Implementation

I used Python and FastAPI to build the Exam Scheduler Service.

The project contains two services:

- Room Booking Service: Provides the available rooms and manages room bookings.
- Exam Scheduler Service: Receives exam requests, checks room availability, and selects a suitable room.

The Room Booking Service runs on port 8001, and the Exam Scheduler Service runs on port 8002.

I also added the "/config" endpoint to display the current configuration, including the service URL, request timeout, and maximum number of retries.

3. Retry Mechanism

I added a retry mechanism to handle temporary problems when communicating with the Room Booking Service.

The scheduler retries requests when a timeout, connection error, or server error (5xx) occurs.

I used Exponential Backoff, where the waiting time increases after each failed attempt:

- First retry: 0.5 seconds.
- Second retry: 1 second.
- Third retry: 2 seconds.

The scheduler does not retry requests when the response is 404 or 409.

To avoid duplicate bookings, I added an Idempotency check in the Room Booking Service. Before creating a new booking, the service checks whether the same exam ID already exists. If it exists, the service returns the existing booking instead of creating another one.

4. Results

The following table shows the three delay and timeout combinations and their corresponding results.

Test| Delay| Timeout| Status Code| Response Time
Test 1| 0.0 s| 2.0 s| 201| —
Test 2| 0.2 s| 1.0 s| 201| —
Test 3| 0.6 s| 0.3 s| 503| —

The first test uses a short delay compared to the timeout, allowing the request to complete successfully.

In the second test, the service takes slightly longer to respond, but the request can still complete successfully within the timeout.

In the third test, the delay is longer than the timeout. The scheduler tries again, but the request cannot complete within the configured retry attempts, so it returns a 503 response.

5. Conclusion

Through this lab, I learned how to build two services that communicate with each other using HTTP requests.

I also learned how to handle timeouts and connection errors using retries and Exponential Backoff. Another important part was using Idempotency to prevent duplicate exam bookings.

Overall, this lab helped me understand how services communicate and how to handle temporary failures in a distributed system.