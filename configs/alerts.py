thresholds:
  cpu_percent: 85
  memory_percent: 90
  disk_percent: 95
  swap_percent: 80

alerts:
  channels:
    - type: console
    - type: logfile
      path: /tmp/infra-monitor-alerts.log
    # - type: webhook
    #   url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL

interval_seconds: 10
cooldown_seconds: 60
retention_seconds: 86400
