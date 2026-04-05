# src/utils/config.py
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "thresholds": {
        "cpu_percent": 85,
        "memory_percent": 90,
        "disk_percent": 95,
    },
    "alerts": {
        "channels": [{"type": "console"}]
    },
    "interval_seconds": 10,
    "cooldown_seconds": 60,
    "retention_seconds": 86400,
}


def load_config(path: str | None = None) -> dict:
    config = DEFAULT_CONFIG.copy()
    if path and Path(path).exists():
        with open(path) as f:
            user = yaml.safe_load(f) or {}
        config.update(user)
    return config
