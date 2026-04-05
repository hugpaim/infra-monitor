# src/alerts/channels.py
import json
import logging
from abc import ABC, abstractmethod
import requests


class BaseChannel(ABC):
    @abstractmethod
    def send(self, alert: dict): ...


class ConsoleChannel(BaseChannel):
    COLORS = {"warning": "\033[33m", "critical": "\033[31m", "info": "\033[36m"}
    RESET = "\033[0m"

    def send(self, alert: dict):
        color = self.COLORS.get(alert["severity"], "")
        print(f"{color}[ALERT {alert['severity'].upper()}] {alert['message']} "
              f"(value={alert['value']}, threshold={alert['threshold']}) "
              f"@ {alert['timestamp']}{self.RESET}")


class LogfileChannel(BaseChannel):
    def __init__(self, path: str):
        self.logger = logging.getLogger("infra_monitor.alerts")
        handler = logging.FileHandler(path)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.WARNING)

    def send(self, alert: dict):
        self.logger.warning(json.dumps(alert))


class WebhookChannel(BaseChannel):
    def __init__(self, url: str, headers: dict | None = None):
        self.url = url
        self.headers = headers or {"Content-Type": "application/json"}

    def send(self, alert: dict):
        payload = {
            "text": f"🚨 *{alert['severity'].upper()}*: {alert['message']} "
                    f"(`{alert['value']}` vs threshold `{alert['threshold']}`)"
        }
        try:
            requests.post(self.url, json=payload, headers=self.headers, timeout=5)
        except requests.RequestException as e:
            print(f"[webhook] failed to send alert: {e}")


def get_channel(config: dict) -> BaseChannel:
    t = config.get("type", "console")
    if t == "console":
        return ConsoleChannel()
    if t == "logfile":
        return LogfileChannel(config.get("path", "/tmp/alerts.log"))
    if t == "webhook":
        return WebhookChannel(config["url"], config.get("headers"))
    raise ValueError(f"Unknown channel type: {t}")
