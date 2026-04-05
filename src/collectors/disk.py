# src/collectors/disk.py
import psutil
from .base import BaseCollector, Metric


class DiskCollector(BaseCollector):
    name = "disk"

    def collect(self) -> list[Metric]:
        metrics = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                metrics += [
                    Metric("disk_total_gb", round(usage.total / 1e9, 2), "GB",
                           labels={"mount": part.mountpoint}),
                    Metric("disk_used_gb", round(usage.used / 1e9, 2), "GB",
                           labels={"mount": part.mountpoint}),
                    Metric("disk_percent", usage.percent, "%",
                           labels={"mount": part.mountpoint}),
                ]
            except PermissionError:
                pass
        io = psutil.disk_io_counters()
        if io:
            metrics += [
                Metric("disk_read_mb", round(io.read_bytes / 1e6, 2), "MB"),
                Metric("disk_write_mb", round(io.write_bytes / 1e6, 2), "MB"),
            ]
        return metrics
