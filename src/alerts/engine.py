
# src/alerts/engine.py
import time
from dataclasses import dataclass
from src.alerts.channels import get_channel


@dataclass
class AlertRule:
    metric_name: str
    threshold: float
    operator: str = ">"          # >, <, >=, <=
    severity: str = "warning"
    message: str = ""

    def evaluate(self, value: float) -> bool:
        ops = {
            ">":  lambda v, t: v > t,
            "<":  lambda v, t: v < t,
            ">=": lambda v, t: v >= t,
            "<=": lambda v, t: v <= t,
        }
        return ops.get(self.operator, ops[">"])(value, self.threshold)


class AlertEngine:
    def __init__(self, config: dict):
        self.rules: list[AlertRule] = self._parse_rules(config)
        self.channels = [get_channel(c) for c in config.get("alerts", {}).get("channels", [])]
        self._cooldown: dict[str, float] = {}
        self.cooldown_seconds = config.get("cooldown_seconds", 60)

    def _parse_rules(self, config: dict) -> list[AlertRule]:
        rules = []
        for metric, threshold in config.get("thresholds", {}).items():
            rules.append(AlertRule(
                metric_name=metric,
                threshold=float(threshold),
                message=f"{metric} exceeded {threshold}",
            ))
        return rules

    def evaluate(self, metrics: dict[str, float]):
        now = time.time()
        for rule in self.rules:
            value = metrics.get(rule.metric_name)
            if value is None:
                continue
            if rule.evaluate(value):
                last_fired = self._cooldown.get(rule.metric_name, 0)
                if now - last_fired >= self.cooldown_seconds:
                    self._fire(rule, value)
                    self._cooldown[rule.metric_name] = now

    def _fire(self, rule: AlertRule, value: float):
        alert = {
            "severity": rule.severity,
            "metric": rule.metric_name,
            "value": value,
            "threshold": rule.threshold,
            "message": rule.message or f"{rule.metric_name}={value} {rule.operator} {rule.threshold}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        for channel in self.channels:
            channel.send(alert)
