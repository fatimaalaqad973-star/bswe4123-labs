from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import sys

start_time = time.time()

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/health":

            time.sleep(delay)

            uptime = time.time() - start_time

            response = {
                "status": "ok",
                "uptime": round(uptime, 2)
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(("127.0.0.1", port), HealthHandler)

print(f"Service running on port {port}")

server.serve_forever()