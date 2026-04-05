# src/collectors/cpu.py
import psutil
from src.collectors.base import BaseCollector, Metric


class CPUCollector(BaseCollector):
    name = "cpu"

    def collect(self) -> list[Metric]:
        percent = psutil.cpu_percent(interval=0.5)
        per_core = psutil.cpu_percent(interval=0, percpu=True)
        freq = psutil.cpu_freq()
        metrics = [
            Metric("cpu_percent", percent, "%"),
            Metric("cpu_count_logical", psutil.cpu_count(), "cores"),
        ]
        if freq:
            metrics.append(Metric("cpu_freq_mhz", round(freq.current, 1), "MHz"))
        for i, c in enumerate(per_core):
            metrics.append(Metric("cpu_core_percent", c, "%", labels={"core": str(i)}))
        return metrics

