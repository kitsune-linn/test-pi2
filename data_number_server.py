from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
from pathlib import Path
import json
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"
PORT = 8001
DATA_FILE = Path(__file__).with_name("simple_numbers.jsonl")


def classify_value(value: float) -> str:
    if 0 <= value <= 3:
        return "off"
    if 4 <= value <= 6:
        return "running"
    if 7 <= value <= 8:
        return "spinning"
    return "unknown"


def save_record(value: float, source: str = "unknown") -> dict:
    record = {
        "value": value,
        "source": source,
        "state": classify_value(value),
    }
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
    def _send_json(self, status_code: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status_code: int, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
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

        if parsed.path == "/":
            self._send_html(
                200,
                """<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Number State Dashboard</title>
        <style>
            :root {
                --bg: #f4f6fb;
                --card: #ffffff;
                --text: #1f2937;
                --muted: #6b7280;
                --border: #e5e7eb;
                --off: #9ca3af;
                --running: #f59e0b;
                --spinning: #22c55e;
            }
            * { box-sizing: border-box; }
            body {
                margin: 0;
                min-height: 100vh;
                font-family: "Segoe UI", Tahoma, sans-serif;
                color: var(--text);
                background: radial-gradient(circle at top right, #dbeafe 0%, var(--bg) 45%);
                padding: 24px;
            }
            .card {
                max-width: 720px;
                margin: 0 auto;
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 16px;
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.06);
                overflow: hidden;
            }
            .header {
                padding: 20px 24px;
                border-bottom: 1px solid var(--border);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            h1 {
                margin: 0;
                font-size: 22px;
            }
            .muted {
                color: var(--muted);
                font-size: 13px;
            }
            button {
                border: 0;
                background: #111827;
                color: #fff;
                padding: 8px 12px;
                border-radius: 8px;
                cursor: pointer;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                text-align: left;
                padding: 14px 24px;
                border-bottom: 1px solid var(--border);
            }
            th {
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: var(--muted);
            }
            .badge {
                display: inline-block;
                min-width: 84px;
                text-align: center;
                padding: 4px 10px;
                border-radius: 999px;
                color: #fff;
                font-weight: 600;
                font-size: 12px;
            }
            .off { background: var(--off); }
            .running { background: var(--running); }
            .spinning { background: var(--spinning); }
            .unknown { background: #ef4444; }
            .empty {
                padding: 28px 24px;
                color: var(--muted);
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <div>
                    <h1>Washine machine state record</h1>
                    <div id="updated" class="muted">Loading...</div>
                </div>
                <button id="refresh">Refresh</button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Value</th>
                        <th>State</th>
                    </tr>
                </thead>
                <tbody id="rows"></tbody>
            </table>
            <div id="empty" class="empty" style="display:none;">No data yet.</div>
        </div>

        <script>
            async function loadTable() {
                const rows = document.getElementById('rows');
                const empty = document.getElementById('empty');
                const updated = document.getElementById('updated');
                rows.innerHTML = '';

                try {
                    const response = await fetch('/numbers?limit=100', { cache: 'no-store' });
                    const data = await response.json();

                    if (!Array.isArray(data) || data.length === 0) {
                        empty.style.display = 'block';
                        updated.textContent = 'No records';
                        return;
                    }

                    empty.style.display = 'none';
                    for (const item of data) {
                        const tr = document.createElement('tr');
                        const valueTd = document.createElement('td');
                        valueTd.textContent = String(item.value ?? '');

                        const stateTd = document.createElement('td');
                        const badge = document.createElement('span');
                        const state = String(item.state ?? 'unknown').toLowerCase();
                        badge.className = 'badge ' + state;
                        badge.textContent = state;
                        stateTd.appendChild(badge);

                        tr.appendChild(valueTd);
                        tr.appendChild(stateTd);
                        rows.appendChild(tr);
                    }

                    updated.textContent = 'Updated: ' + new Date().toLocaleString();
                } catch (error) {
                    empty.style.display = 'block';
                    empty.textContent = 'Cannot load data from /numbers';
                    updated.textContent = 'Load failed';
                }
            }

            document.getElementById('refresh').addEventListener('click', loadTable);
            loadTable();
        </script>
    </body>
</html>
""",
            )
            return

        if parsed.path == "/health":
            self._send_json(200, {"status": "ok", "port": PORT})
            return

        if parsed.path == "/numbers":
            query = parse_qs(parsed.query)
            limit = int(query.get("limit", ["20"])[0])
            records = load_records(limit=limit)
            table = [
                {"value": r["value"], "state": r.get("state", classify_value(r["value"]))}
                for r in records
            ]
            self._send_json(200, table)
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
