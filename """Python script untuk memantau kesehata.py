"""Python script untuk memantau kesehatan dan performa MySQL secara real-time.

Install library yang dibutuhkan:
    pip install mysql-connector-python matplotlib

Gunakan host: localhost, port: 3306, user: root.
"""

import time
from collections import deque

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("Warning: mysql-connector-python not installed. Install with: pip install mysql-connector-python")
    mysql = None
    Error = Exception

try:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
except ImportError:
    print("Warning: matplotlib not installed. Install with: pip install matplotlib")
    plt = None
    FuncAnimation = None

# Konfigurasi koneksi database
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",  # Ganti jika MySQL root memiliki password
    "connection_timeout": 5,
}

# Interval polling dalam milidetik
POLL_INTERVAL_MS = 2000
# Jumlah titik data yang ditampilkan di grafik
MAX_POINTS = 60


def safe_connect():
    """Mencoba membuat koneksi ke MySQL dan mengembalikan objek koneksi."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as exc:
        print("Koneksi MySQL gagal:", exc)
    return None


def fetch_global_status(conn):
    """Mengambil status global MySQL menggunakan SHOW GLOBAL STATUS."""
    cursor = conn.cursor()
    cursor.execute("SHOW GLOBAL STATUS")
    status = {}
    for name, value in cursor:
        try:
            status[name] = int(value)
        except (ValueError, TypeError):
            status[name] = 0
    cursor.close()
    return status


def get_metrics(conn, prev_totals, prev_time):
    """Menghitung metrik koneksi dan query per detik dari MySQL."""
    status = fetch_global_status(conn)
    now = time.time()
    interval = now - prev_time if prev_time else POLL_INTERVAL_MS / 1000.0
    query_total = sum(
        status.get(key, 0)
        for key in ("Com_select", "Com_insert", "Com_update", "Com_delete")
    )
    prev_total = prev_totals.get("queries", query_total)
    qps = (query_total - prev_total) / interval if interval > 0 else 0.0

    metrics = {
        "connections": status.get("Threads_connected", 0),
        "query_rate": max(qps, 0.0),
        "health": 1.0,
    }
    return metrics, {"queries": query_total}, now


def init_plots():
    """Menyiapkan figure dan axes untuk grafik."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), constrained_layout=True)

    ax_conn, ax_qps, ax_health = axes
    ax_conn.set_title("Grafik Koneksi MySQL")
    ax_conn.set_ylabel("Jumlah Koneksi")
    ax_conn.set_xlim(0, MAX_POINTS)
    ax_conn.set_ylim(0, 10)
    ax_conn.grid(True, linestyle="--", alpha=0.4)

    ax_qps.set_title("Grafik Kecepatan Query (Select/Insert/Update/Delete per detik)")
    ax_qps.set_ylabel("Query / detik")
    ax_qps.set_xlim(0, MAX_POINTS)
    ax_qps.set_ylim(0, 10)
    ax_qps.grid(True, linestyle="--", alpha=0.4)

    ax_health.set_title("Grafik Status Up/Down MySQL")
    ax_health.set_ylabel("Status")
    ax_health.set_xlabel("Waktu (frame)")
    ax_health.set_xlim(0, MAX_POINTS)
    ax_health.set_ylim(-0.1, 1.1)
    ax_health.grid(True, linestyle="--", alpha=0.4)
    ax_health.set_yticks([0, 1])
    ax_health.set_yticklabels(["Down", "Up"])

    line_conn, = ax_conn.plot([], [], color="tab:blue", linewidth=2)
    line_qps, = ax_qps.plot([], [], color="tab:green", linewidth=2)
    line_health, = ax_health.step([], [], where="mid", color="tab:red", linewidth=2)

    text_conn = ax_conn.text(
        0.98, 0.95, "", transform=ax_conn.transAxes,
        ha="right", va="top", fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7)
    )

    text_qps = ax_qps.text(
        0.98, 0.95, "", transform=ax_qps.transAxes,
        ha="right", va="top", fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7)
    )

    text_health = ax_health.text(
        0.98, 0.95, "", transform=ax_health.transAxes,
        ha="right", va="top", fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7)
    )

    return (
        fig,
        ax_conn,
        ax_qps,
        ax_health,
        line_conn,
        line_qps,
        line_health,
        text_conn,
        text_qps,
        text_health,
    )


def main():
    """Fungsi utama untuk menjalankan monitoring dan animasi grafik."""
    conn = safe_connect()
    prev_totals = {}
    prev_time = None

    timestamps = deque(maxlen=MAX_POINTS)
    conn_values = deque(maxlen=MAX_POINTS)
    qps_values = deque(maxlen=MAX_POINTS)
    health_values = deque(maxlen=MAX_POINTS)

    (
        fig,
        ax_conn,
        ax_qps,
        ax_health,
        line_conn,
        line_qps,
        line_health,
        text_conn,
        text_qps,
        text_health,
    ) = init_plots()

    def animate(frame):
        nonlocal conn, prev_totals, prev_time
        health_state = 0
        metrics = {"connections": 0, "query_rate": 0.0, "health": 0.0}

        if conn is None or not conn.is_connected():
            conn = safe_connect()

        try:
            if conn is not None and conn.is_connected():
                metrics, prev_totals, prev_time = get_metrics(conn, prev_totals, prev_time)
                health_state = 1
        except Error as exc:
            print("Gagal mengambil metrik MySQL:", exc)
            conn = None
            health_state = 0

        timestamps.append(time.strftime("%H:%M:%S"))
        conn_values.append(metrics["connections"])
        qps_values.append(metrics["query_rate"])
        health_values.append(health_state)

        x = list(range(len(timestamps)))

        line_conn.set_data(x, list(conn_values))
        line_qps.set_data(x, list(qps_values))
        line_health.set_data(x, list(health_values))

        ax_conn.set_xlim(0, MAX_POINTS)
        ax_qps.set_xlim(0, MAX_POINTS)
        ax_health.set_xlim(0, MAX_POINTS)

        ax_conn.set_ylim(0, max(max(conn_values, default=1) * 1.2, 5))
        ax_qps.set_ylim(0, max(max(qps_values, default=1) * 1.2, 5))

        text_conn.set_text(f"Koneksi saat ini: {metrics['connections']}")
        text_qps.set_text(f"QPS: {metrics['query_rate']:.2f}")
        text_health.set_text("Status: Up" if health_state else "Status: Down")

        return line_conn, line_qps, line_health, text_conn, text_qps, text_health

    ani = FuncAnimation(fig, animate, interval=POLL_INTERVAL_MS, blit=True)
    plt.suptitle("Monitoring Kesehatan dan Performa MySQL")
    plt.show()


if __name__ == "__main__":
    main()
