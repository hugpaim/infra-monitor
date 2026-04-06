# 🖥️ infra-monitor

> Real-time infrastructure monitoring with terminal dashboard, threshold alerting, and Prometheus metrics export.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white)
![Rich](https://img.shields.io/badge/Rich-TUI-000000?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![CI](https://github.com/hugpaim/infra-monitor/actions/workflows/ci.yml/badge.svg)

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────┐
│         Collectors (psutil)                         │
│   CPU │ Memory │ Disk │ Network │ Processes          │
└──────────────────────┬──────────────────────────────┘
                       │
         ┌─────────────▼─────────────┐
         │      MetricsStore         │
         │        (SQLite)           │
         └──────┬──────────┬─────────┘
                │          │
   ┌────────────▼──┐  ┌────▼──────────────────┐
   │   Dashboard   │  │     AlertEngine        │
   │  (Rich Live)  │  │  threshold evaluation  │
   └───────────────┘  └────┬─────────────┬─────┘
                           │             │
                    ┌──────▼──┐  ┌───────▼─────────┐
                    │ Console │  │ Webhook / Logfile│
                    └─────────┘  └─────────────────┘
                                        │
                       ┌────────────────▼────────────┐
                       │     PrometheusExporter       │
                       │        :9100/metrics         │
                       └──────────────────────────────┘
```

## 📁 Project Structure

```
infra-monitor/
├── src/
│   ├── collectors/
│   │   ├── base.py           # BaseCollector ABC
│   │   ├── cpu.py
│   │   ├── memory.py
│   │   ├── disk.py
│   │   ├── network.py
│   │   └── processes.py
│   ├── alerts/
│   │   ├── engine.py         # Threshold evaluation loop
│   │   └── channels.py       # Console / Webhook / Logfile
│   ├── dashboard/
│   │   └── live.py           # Rich Live terminal dashboard
│   ├── utils/
│   │   ├── config.py         # YAML config loader
│   │   ├── store.py          # SQLite metrics store
│   │   └── prometheus.py     # HTTP metrics exporter
│   └── main.py               # CLI entrypoint (Click)
├── configs/
│   └── alerts.yaml           # Thresholds and alert channels
├── tests/
│   ├── test_collectors.py
│   └── test_alerts.py
├── conftest.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/hugpaim/infra-monitor.git
cd infra-monitor

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run live terminal dashboard
python -m src.main dashboard
```

## ⚙️ Commands

| Command | Description |
|---------|-------------|
| `python -m src.main dashboard` | Launch real-time terminal dashboard |
| `python -m src.main export --port 9100` | Start Prometheus metrics exporter |
| `python -m src.main daemon --config configs/alerts.yaml` | Run alert evaluation daemon |

## 🔔 Alert Configuration

Edit `configs/alerts.yaml` to set thresholds and notification channels:

```yaml
thresholds:
  cpu_percent: 85
  memory_percent: 90
  disk_percent: 95

alerts:
  channels:
    - type: console
    - type: logfile
      path: /tmp/infra-monitor-alerts.log
    - type: webhook
      url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL

interval_seconds: 10
cooldown_seconds: 60
```

## 📊 Prometheus Integration

Start the exporter and point Prometheus at `:9100/metrics`:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: infra-monitor
    static_configs:
      - targets: ['localhost:9100']
```

Metrics exposed include `infra_cpu_percent`, `infra_memory_percent`, `infra_disk_percent`, `infra_net_bytes_recv_mb`, and more.

## 🧪 Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

```
tests/test_collectors.py::test_cpu_collector_returns_metrics  PASSED
tests/test_collectors.py::test_memory_collector               PASSED
tests/test_collectors.py::test_disk_collector                 PASSED
tests/test_collectors.py::test_network_collector              PASSED
tests/test_collectors.py::test_process_collector              PASSED
tests/test_alerts.py::test_alert_rule_greater_than            PASSED
tests/test_alerts.py::test_alert_rule_less_than               PASSED
tests/test_alerts.py::test_alert_engine_fires                 PASSED
tests/test_alerts.py::test_alert_engine_cooldown              PASSED

9 passed
```

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Metrics collection | Python / psutil |
| Terminal UI | Rich |
| CLI | Click |
| Alerting | Custom engine + webhooks |
| Metrics export | Prometheus-compatible HTTP |
| Storage | SQLite |
| Config | YAML |

---

> Part of [@hugpaim](https://github.com/hugpaim) DevOps portfolio
