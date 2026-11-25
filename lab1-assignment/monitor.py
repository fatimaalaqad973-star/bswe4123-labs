import httpx
import time

services = {
    "Service 1": "http://127.0.0.1:8001/health",
    "Service 2": "http://127.0.0.1:8002/health",
    "Service 3": "http://127.0.0.1:8003/health"
}

timeout = 1.5
slow_limit = 500
failure_limit = 3
check_interval = 2
monitor_duration = 60

failures = {name: 0 for name in services}

start_time = time.monotonic()

with httpx.Client(timeout=timeout, trust_env=False) as client:

    while time.monotonic() - start_time < monitor_duration:

        print("\n--- Health Monitor ---")

        for name, url in services.items():

            try:
                request_start = time.perf_counter()

                response = client.get(url)
                response.raise_for_status()

                elapsed = (time.perf_counter() - request_start) * 1000

                failures[name] = 0

                if elapsed > slow_limit:
                    print(f"{name}: SLOW ({elapsed:.2f} ms)")
                else:
                    print(f"{name}: UP ({elapsed:.2f} ms)")

            except (httpx.RequestError, httpx.HTTPStatusError):

                failures[name] += 1

                if failures[name] >= failure_limit:
                    print(f"{name}: DOWN")
                else:
                    print(f"{name}: CHECKING ({failures[name]}/3)")

        time.sleep(check_interval)

print("\nMonitoring finished.")