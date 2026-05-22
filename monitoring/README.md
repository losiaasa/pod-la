Monitoring stack for MySQL using mysqld_exporter, Prometheus and Grafana

Overview
--------
This folder contains configuration to run a monitoring stack alongside your application stack. It includes:

- `docker-compose.monitoring.yml` : Compose file to start Prometheus, Grafana and mysqld_exporter
- `monitoring/prometheus/prometheus.yml` : Prometheus scrape config
- `monitoring/grafana/provisioning/...` : Grafana provisioning for datasource and dashboards

Quick start
-----------
1. Copy `docker-compose.monitoring.yml` into your project root (already placed at repository root).
2. Create an exporter user in MySQL (run as `root` on your MySQL server):

```sql
CREATE USER 'exporter'@'%' IDENTIFIED BY 'StrongExporterPassword';
GRANT PROCESS, REPLICATION CLIENT ON *.* TO 'exporter'@'%';
GRANT SELECT ON performance_schema.* TO 'exporter'@'%';
GRANT SELECT ON sys.* TO 'exporter'@'%';
FLUSH PRIVILEGES;
```

3. Edit `docker-compose.monitoring.yml` and replace `REPLACE_EXPORTER_PASSWORD` with the password you set above. Also replace `mysql` in DSN if your MySQL service name is different.

4. Start the monitoring stack (run from repository root):

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

If you don't want to combine files, run only the monitoring compose:

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

5. Open Grafana at http://localhost:3000 (admin/admin). The datasource to Prometheus is provisioned automatically.

Importing dashboards
--------------------
- You can import ready-made Grafana dashboards from https://grafana.com/dashboards by searching for "MySQL" or "mysqld exporter".
- In Grafana UI: Dashboards -> Import -> paste dashboard ID or JSON.

Recommended dashboards (search on grafana.com):
- "MySQL Overview"
- "MySQL Metrics (by Prometheus)"
- "Percona MySQL Overview"

Notes & recommendations
-----------------------
- For production, change Grafana admin password (`GF_SECURITY_ADMIN_PASSWORD`) and secure credentials via Docker secrets or env files.
- For remote MySQL instances, enable SSL and restrict exporter user privileges and allowed hosts.
- Consider adding `node_exporter` to monitor host-level metrics (disk, memory, CPU).

Optional: Provision dashboards automatically
------------------------------------------
- Drop JSON dashboard files into `monitoring/grafana/dashboards/` — they will be imported on Grafana startup because of provisioning config.

Need help importing a specific dashboard ID automatically? Saya bisa ambil JSON dashboard dari grafana.com dan letakkan di `monitoring/grafana/dashboards/` jika Anda berikan ID yang diinginkan.
