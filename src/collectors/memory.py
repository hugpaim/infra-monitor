# src/collectors/memory.py
import psutil
from .base import BaseCollector, Metric


class MemoryCollector(BaseCollector):
    name = "memory"

    def collect(self) -> list[Metric]:
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return [
            Metric("memory_total_mb", round(vm.total / 1024 / 1024, 1), "MB"),
            Metric("memory_used_mb", round(vm.used / 1024 / 1024, 1), "MB"),
            Metric("memory_available_mb", round(vm.available / 1024 / 1024, 1), "MB"),
            Metric("memory_percent", vm.percent, "%"),
            Metric("swap_total_mb", round(swap.total / 1024 / 1024, 1), "MB"),
            Metric("swap_used_mb", round(swap.used / 1024 / 1024, 1), "MB"),
            Metric("swap_percent", swap.percent, "%"),
        ]
