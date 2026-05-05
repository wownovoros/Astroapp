import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._cors_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            birthdate = body.get('birthdate', '')
            from services.natal import build_natal_report
            report = build_natal_report(birthdate)
            result = {'report': report}
        except Exception as e:
            result = {'error': str(e)}
        self._respond(result)

    def _cors_headers(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _respond(self, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)
