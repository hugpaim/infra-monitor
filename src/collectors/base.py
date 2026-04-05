# src/collectors/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import time


@dataclass
class Metric:
    name: str
    value: float | int | str
    unit: str = ""
    labels: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class BaseCollector(ABC):
    """Abstract base class for all metric collectors."""

    name: str = "base"

    @abstractmethod
    def collect(self) -> list[Metric]:
        """Collect and return a list of Metric objects."""
        ...

    def safe_collect(self) -> list[Metric]:
        """Wrapper with error handling."""
        try:
            return self.collect()
        except Exception as exc:
            print(f"[{self.name}] collection error: {exc}")
            return []
