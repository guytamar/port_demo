# Observability: Prometheus + Grafana

This project includes a minimal observability stack (Prometheus + Grafana) and instrumentation for the Flask server.

What was added
- `/metrics` endpoint on the Flask server (using `prometheus-client`).
- Basic request metrics: `flask_http_requests_total`, `flask_request_latency_seconds`, `flask_exceptions_total`.
- `docker-compose.observability.yml` to run Prometheus and Grafana locally.
- Prometheus scrape config at `monitoring/prometheus.yml` (scrapes `host.docker.internal:5100/metrics`).
- Grafana provisioning (datasource + dashboards) and a sample SLO dashboard at `monitoring/grafana/dashboards/slo_dashboard.json`.

Quick start
1. Install Python dependencies (server):

```bash
# from project root (on Windows use PowerShell or Git Bash)
./scripts/setup-env.sh
```

2. Start the Flask server (in development):

```bash
# from project root
python server/app.py
```

3. Start the observability stack:

```bash
docker-compose -f docker-compose.observability.yml up -d
```

4. Open Prometheus: http://localhost:9090
   Open Grafana: http://localhost:3000 (username: `admin`, password: `admin`)

Importing the dashboard
- The included dashboard is auto-provisioned by Grafana (provisioning files are in `monitoring/grafana/provisioning`).
- If provisioning is disabled or you want to import manually: in Grafana, go to "+" → "Import" and paste the JSON from `monitoring/grafana/dashboards/slo_dashboard.json`.

SLO ideas and Prometheus queries
- Availability (%):
  (1 - (sum(rate(flask_exceptions_total[5m])) / sum(rate(flask_http_requests_total[5m])))) * 100
- Latency P95 (seconds):
  histogram_quantile(0.95, sum(rate(flask_request_latency_seconds_bucket[5m])) by (le))
- Request rate (RPS):
  sum(rate(flask_http_requests_total[5m]))

Notes
- The Prometheus config scrapes `host.docker.internal:5100` so the Flask server can run on the host. If you containerize the Flask service, update the `scrape_configs` target to the container service name.
- Adjust histogram buckets in code if you need different latency resolution.

Next steps I can help with
- Add OpenTelemetry traces and a trace UI (Jaeger/Tempo).
- Create richer Grafana SLO panels and alerting rules.
- Containerize the Flask app so Prometheus scrapes the container network directly.
