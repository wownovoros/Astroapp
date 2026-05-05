import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import BaseHTTPRequestHandler
import json
import urllib.parse


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._cors_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        sign = params.get('sign', [''])[0]
        htype = params.get('type', ['day'])[0]
        try:
            from services.parser import get_daily_horoscope, get_weekly_horoscope
            text = get_weekly_horoscope(sign) if htype == 'week' else get_daily_horoscope(sign)
            result = {'text': text}
        except Exception as e:
            result = {'error': str(e)}
        self._respond(result)

    def _cors_headers(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _respond(self, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)
