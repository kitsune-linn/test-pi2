from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
from pathlib import Path
import json
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"
PORT = 8001
DATA_FILE = Path(__file__).with_name("simple_numbers.jsonl")


def save_record(value: float, source: str = "unknown") -> dict:
    record = {"value": value}
    with DATA_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_records(limit: int = 20) -> list[dict]:
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    records = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


class NumberHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._send_json(200, {"status": "ok", "port": PORT})
            return

        if parsed.path == "/numbers":
            query = parse_qs(parsed.query)
            limit = int(query.get("limit", ["20"])[0])
            records = load_records(limit=limit)
            values = [r["value"] for r in records]
            self._send_json(200, {"count": len(values), "values": values})
            return

        self._send_json(
            200,
            {
                "message": "Simple number server is running",
                "endpoints": {
                    "health": "GET /health",
                    "list": "GET /numbers?limit=20",
                    "post_json": "POST /number with JSON {\"value\": 12.3}",
                    "post_text": "POST /number with plain text like 12.3",
                },
            },
        )

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/number":
            self._send_json(404, {"error": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8").strip()
        content_type = self.headers.get("Content-Type", "")

        try:
            if "application/json" in content_type:
                payload = json.loads(raw_body or "{}")
                value = float(payload["value"])
                source = str(payload.get("source", "json"))
            else:
                value = float(raw_body)
                source = "text"
        except (ValueError, KeyError, json.JSONDecodeError):
            self._send_json(400, {"error": "Invalid number payload"})
            return

        record = save_record(value=value, source=source)
        self._send_json(201, {"success": True, "record": record})

    def log_message(self, format: str, *args) -> None:
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), NumberHandler)
    print(f"Simple number server running at http://127.0.0.1:{PORT}")
    print("POST number to /number, GET saved data from /numbers")
    server.serve_forever()
