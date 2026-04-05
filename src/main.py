# src/main.py
import time
import click
from src.utils.config import load_config
from src.utils.store import MetricsStore
from src.utils.prometheus import PrometheusExporter
from src.alerts.engine import AlertEngine
from src.collectors.cpu import CPUCollector
from src.collectors.memory import MemoryCollector
from src.collectors.disk import DiskCollector
from src.collectors.network import NetworkCollector
from src.collectors.processes import ProcessCollector

ALL_COLLECTORS = [
    CPUCollector(),
    MemoryCollector(),
    DiskCollector(),
    NetworkCollector(),
    ProcessCollector(),
]


@click.group()
def cli():
    """infra-monitor — Infrastructure monitoring tool."""
    pass


@cli.command()
@click.option("--interval", default=2, show_default=True, help="Refresh interval in seconds")
def dashboard(interval):
    """Launch the real-time terminal dashboard."""
    from src.dashboard.live import run_dashboard
    run_dashboard(interval=interval)


@cli.command()
@click.option("--port", default=9100, show_default=True, help="HTTP port for /metrics")
@click.option("--interval", default=15, show_default=True, help="Scrape interval seconds")
def export(port, interval):
    """Run Prometheus metrics exporter."""
    exporter = PrometheusExporter(port=port)
    exporter.start()
    click.echo(f"[export] scraping every {interval}s")
    while True:
        metrics = []
        for col in ALL_COLLECTORS:
            metrics.extend(col.safe_collect())
        exporter.update(metrics)
        time.sleep(interval)


@cli.command()
@click.option("--config", default="configs/alerts.yaml", show_default=True)
@click.option("--interval", default=10, show_default=True)
def daemon(config, interval):
    """Run alert evaluation daemon."""
    cfg = load_config(config)
    engine = AlertEngine(cfg)
    store = MetricsStore()
    click.echo(f"[daemon] running (interval={interval}s)")
    while True:
        metrics_flat = {}
        all_metrics = []
        for col in ALL_COLLECTORS:
            for m in col.safe_collect():
                all_metrics.append(m)
                if isinstance(m.value, (int, float)) and not m.labels:
                    metrics_flat[m.name] = float(m.value)
        store.save(all_metrics)
        engine.evaluate(metrics_flat)
        time.sleep(interval)


if __name__ == "__main__":
    cli()
