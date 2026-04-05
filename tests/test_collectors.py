# tests/test_collectors.py
import pytest
from src.collectors.cpu import CPUCollector
from src.collectors.memory import MemoryCollector
from src.collectors.disk import DiskCollector
from src.collectors.network import NetworkCollector
from src.collectors.processes import ProcessCollector
from src.collectors.base import Metric


def test_cpu_collector_returns_metrics():
    metrics = CPUCollector().collect()
    names = [m.name for m in metrics]
    assert "cpu_percent" in names
    assert "cpu_count_logical" in names
    for m in metrics:
        assert isinstance(m, Metric)


def test_memory_collector():
    metrics = MemoryCollector().collect()
    names = [m.name for m in metrics]
    assert "memory_percent" in names
    assert "memory_used_mb" in names
    pct = next(m for m in metrics if m.name == "memory_percent")
    assert 0 <= float(pct.value) <= 100


def test_disk_collector():
    metrics = DiskCollector().collect()
    assert len(metrics) > 0
    for m in metrics:
        assert isinstance(m.value, (int, float))


def test_network_collector():
    metrics = NetworkCollector().collect()
    names = [m.name for m in metrics]
    assert "net_connections" in names


def test_process_collector():
    metrics = ProcessCollector().collect()
    names = [m.name for m in metrics]
    assert "proc_total" in names
    total = next(m for m in metrics if m.name == "proc_total")
    assert int(total.value) > 0
