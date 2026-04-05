# src/collectors/network.py
import psutil
from .base import BaseCollector, Metric


class NetworkCollector(BaseCollector):
    name = "network"
    _prev: dict = {}

    def collect(self) -> list[Metric]:
        metrics = []
        counters = psutil.net_io_counters(pernic=True)
        for nic, stats in counters.items():
            if nic.startswith("lo"):
                continue
            metrics += [
                Metric("net_bytes_sent_mb", round(stats.bytes_sent / 1e6, 2), "MB",
                       labels={"nic": nic}),
                Metric("net_bytes_recv_mb", round(stats.bytes_recv / 1e6, 2), "MB",
                       labels={"nic": nic}),
                Metric("net_packets_sent", stats.packets_sent, "pkt",
                       labels={"nic": nic}),
                Metric("net_packets_recv", stats.packets_recv, "pkt",
                       labels={"nic": nic}),
                Metric("net_errin", stats.errin, "err", labels={"nic": nic}),
                Metric("net_errout", stats.errout, "err", labels={"nic": nic}),
            ]
        conns = len(psutil.net_connections(kind="inet"))
        metrics.append(Metric("net_connections", conns, "conns"))
        return metrics
