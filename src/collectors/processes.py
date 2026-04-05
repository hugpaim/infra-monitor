# src/collectors/processes.py
import psutil
from src.collectors.base import BaseCollector, Metric


class ProcessCollector(BaseCollector):
    name = "processes"

    def collect(self) -> list[Metric]:
        procs = list(psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]))
        total = len(procs)
        running = sum(1 for p in procs if p.info["status"] == "running")
        sleeping = sum(1 for p in procs if p.info["status"] == "sleeping")

        top_cpu = sorted(
            procs, key=lambda p: p.info["cpu_percent"] or 0, reverse=True
        )[:5]

        metrics = [
            Metric("proc_total", total, "procs"),
            Metric("proc_running", running, "procs"),
            Metric("proc_sleeping", sleeping, "procs"),
        ]
        for p in top_cpu:
            metrics.append(
                Metric("proc_cpu_percent", p.info["cpu_percent"] or 0, "%",
                       labels={"name": p.info["name"], "pid": str(p.info["pid"])})
            )
        return metrics
