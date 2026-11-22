Lab Assignment 1: Is the Service Up, Slow or Down?
1. Project Description
This project is a simple health monitoring system developed using Python.
The system monitors three services running on ports 8001, 8002, and 8003.
Each service provides a /health endpoint that returns its status and uptime.
2. Service States
The monitor identifies three service states:
UP: The service responds within 500 milliseconds.
SLOW: The service responds after more than 500 milliseconds.
DOWN: The service does not respond after three consecutive failed checks.
3. Monitoring Configuration
The monitoring system uses the following settings:
Check interval: 2 seconds.
Timeout: 1.5 seconds.
Slow threshold: 500 milliseconds.
Failed checks before DOWN: 3.
Monitoring duration: 60 seconds.
4. Step 3: Testing and Observations
The monitoring system is designed to handle different service conditions.
When all services respond quickly, their state is UP.
When a service takes 0.8 seconds to respond, its state becomes SLOW.
When a service is stopped, failed checks are counted until it becomes DOWN.
When the stopped service starts again, its state returns to UP after a successful response.
Monitor Output
Actual monitoring output should be inserted here after running the experiment.
5. Step 4: Consecutive Failed Checks
A single failed check does not necessarily mean that a service is DOWN.
The monitor requires three consecutive failed checks before declaring a service DOWN.
Timeout Choice
The timeout is set to 1.5 seconds.
This gives services enough time to respond while preventing the monitor from waiting too long.
A shorter timeout detects failures faster but may cause false alerts. A longer timeout reduces false alerts but delays failure detection.
Number of Failed Checks
Three consecutive failed checks are required before declaring a service DOWN.
This helps avoid false alerts caused by temporary network problems.
Advantages
Reduces false DOWN alerts.
Handles temporary network problems.
Improves monitoring reliability.
Disadvantages
Failure detection takes longer.
A failed service may not be reported as DOWN immediately.
6. Conclusion
This project demonstrates how Python and HTTPX can be used to monitor multiple services, measure response times, identify service states, and detect failures using consecutive checks.