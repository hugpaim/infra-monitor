# src/utils/prometheus.py
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from src.collectors.base import Metric


class PrometheusExporter:
    def __init__(self, port: int = 9100):
        self.port = port
        self._metrics: list[Metric] = []
        self._lock = threading.Lock()

    def update(self, metrics: list[Metric]):
        with self._lock:
            self._metrics = metrics

    def _render(self) -> str:
        lines = []
        with self._lock:
            for m in self._metrics:
                if not isinstance(m.value, (int, float)):
                    continue
                label_str = ""
                if m.labels:
                    parts = ",".join(f'{k}="{v}"' for k, v in m.labels.items())
                    label_str = f"{{{parts}}}"
                lines.append(f"infra_{m.name}{label_str} {m.value}")
        return "\n".join(lines) + "\n"

    def start(self):
        exporter = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/metrics":
                    body = exporter._render().encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; version=0.0.4")
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, *args):
                pass  # suppress access logs

        server = HTTPServer(("0.0.0.0", self.port), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"[prometheus] exporter running on :{self.port}/metrics")
