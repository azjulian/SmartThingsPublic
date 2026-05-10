#!/usr/bin/env python3
"""
Winderoo Dashboard Server
Run on any computer on the same Wi-Fi as your Winderoo device.

    python3 server.py

Then open http://<this-computer-ip>:8080 on your iPad.
"""

import http.server
import urllib.request
import urllib.error
import json
import os
import socket

WINDEROO = "http://winderoo.local"
PORT = 8080


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)

    def do_GET(self):
        if self.path == "/api/status":
            self._proxy(f"{WINDEROO}/status")
        elif self.path == "/api/reset":
            self._proxy(f"{WINDEROO}/reset")
        else:
            super().do_GET()

    def _proxy(self, url):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.URLError as e:
            msg = json.dumps({"error": str(e.reason)}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

    def log_message(self, fmt, *args):
        pass  # silence request noise


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "your-computer-ip"


if __name__ == "__main__":
    ip = local_ip()
    print(f"\n  Winderoo Dashboard")
    print(f"  ------------------")
    print(f"  Proxying:  {WINDEROO}")
    print(f"  Open on iPad:  http://{ip}:{PORT}\n")
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as srv:
        srv.serve_forever()
