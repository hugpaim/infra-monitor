# tests/test_alerts.py
import pytest
from src.alerts.engine import AlertEngine, AlertRule


def test_alert_rule_greater_than():
    rule = AlertRule("cpu_percent", 80, ">")
    assert rule.evaluate(90) is True
    assert rule.evaluate(70) is False
    assert rule.evaluate(80) is False


def test_alert_rule_less_than():
    rule = AlertRule("free_mem", 10, "<")
    assert rule.evaluate(5) is True
    assert rule.evaluate(15) is False


def test_alert_engine_fires(capsys):
    config = {
        "thresholds": {"cpu_percent": 50},
        "alerts": {"channels": [{"type": "console"}]},
        "cooldown_seconds": 0,
    }
    engine = AlertEngine(config)
    engine.evaluate({"cpu_percent": 99.0})
    captured = capsys.readouterr()
    assert "ALERT" in captured.out or "cpu_percent" in captured.out


def test_alert_engine_cooldown(capsys):
    config = {
        "thresholds": {"cpu_percent": 50},
        "alerts": {"channels": [{"type": "console"}]},
        "cooldown_seconds": 9999,
    }
    engine = AlertEngine(config)
    engine.evaluate({"cpu_percent": 99.0})
    out1 = capsys.readouterr().out
    engine.evaluate({"cpu_percent": 99.0})
    out2 = capsys.readouterr().out
    # Second evaluation should be suppressed by cooldown
    assert len(out2) < len(out1)
