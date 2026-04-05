
# src/dashboard/live.py
import time
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import BarColumn, Progress, TextColumn
from rich import box
from src.collectors.cpu import CPUCollector
from src.collectors.memory import MemoryCollector
from src.collectors.disk import DiskCollector
from src.collectors.network import NetworkCollector
from src.collectors.processes import ProcessCollector

ALL_COLLECTORS = [CPUCollector(), MemoryCollector(), DiskCollector(), NetworkCollector(), ProcessCollector()]
from src.collectors.base import Metric


console = Console()


def _bar(value: float, max_val: float = 100, width: int = 20) -> str:
    filled = int(value / max_val * width)
    bar = "█" * filled + "░" * (width - filled)
    color = "green" if value < 70 else "yellow" if value < 90 else "red"
    return f"[{color}]{bar}[/{color}] {value:.1f}%"


def _collect_all() -> dict[str, Metric]:
    result = {}
    for collector in ALL_COLLECTORS:
        for m in collector.safe_collect():
            result[m.name] = m
    return result


def _build_table(metrics: dict[str, Metric]) -> Table:
    def v(name: str, default="-"):
        m = metrics.get(name)
        return f"{m.value}{m.unit}" if m else str(default)

    def fv(name: str, default=0.0) -> float:
        m = metrics.get(name)
        return float(m.value) if m else default

    table = Table(box=box.ROUNDED, border_style="bright_black", expand=True)
    table.add_column("Metric", style="bold cyan", width=28)
    table.add_column("Value / Chart", min_width=40)

    table.add_row("[bold]CPU[/bold]", "")
    table.add_row("  Overall", _bar(fv("cpu_percent")))
    if "cpu_freq_mhz" in metrics:
        table.add_row("  Frequency", v("cpu_freq_mhz"))
    table.add_row("  Cores", v("cpu_count_logical"))

    table.add_row("", "")
    table.add_row("[bold]Memory[/bold]", "")
    table.add_row("  RAM Usage", _bar(fv("memory_percent")))
    table.add_row("  Used / Total",
                  f"{v('memory_used_mb')} / {v('memory_total_mb')}")
    table.add_row("  Swap Usage", _bar(fv("swap_percent")))

    table.add_row("", "")
    table.add_row("[bold]Disk[/bold]", "")
    for name, m in metrics.items():
        if name == "disk_percent" and not m.labels:
            table.add_row("  Root Usage", _bar(fv("disk_percent")))

    table.add_row("", "")
    table.add_row("[bold]Network[/bold]", "")
    table.add_row("  Connections", v("net_connections"))
    table.add_row("  Sent",  v("net_bytes_sent_mb"))
    table.add_row("  Recv",  v("net_bytes_recv_mb"))

    table.add_row("", "")
    table.add_row("[bold]Processes[/bold]", "")
    table.add_row("  Total",    v("proc_total"))
    table.add_row("  Running",  v("proc_running"))
    table.add_row("  Sleeping", v("proc_sleeping"))

    return table


def run_dashboard(interval: int = 2):
    with Live(console=console, refresh_per_second=1, screen=True) as live:
        while True:
            metrics = _collect_all()
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            panel = Panel(
                _build_table(metrics),
                title=f"[bold green]🖥  infra-monitor[/bold green]  [dim]{ts}[/dim]",
                subtitle="[dim]Ctrl+C to exit[/dim]",
                border_style="green",
            )
            live.update(panel)
            time.sleep(interval)
