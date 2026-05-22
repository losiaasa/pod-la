#!/usr/bin/env python3
"""
Script untuk menjalankan AUTO-UPDATE query berkala dan export hasil ke CSV
Menggunakan MySQL connector untuk koneksi database.
"""

import mysql.connector
import pandas as pd
import os
import sys
from datetime import datetime
import time
import logging

# ============================================================================
# KONFIGURASI
# ============================================================================
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'rahasia123',  # GANTI dengan password Anda
    'database': 'latihan_db'
}

OUTPUT_DIR = '/home/kayto/rui/query_results'
LOG_FILE = '/home/kayto/rui/auto_update.log'

# Buat direktori output jika belum ada
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# FUNGSI KONEKSI DATABASE
# ============================================================================
def get_db_connection():
    """Buat koneksi ke database MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logger.info("Koneksi database berhasil")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Gagal koneksi: {err}")
        sys.exit(1)

# ============================================================================
# FUNGSI UPDATE SUMMARY (JALANKAN PROCEDURE)
# ============================================================================
def run_update_procedures():
    """Jalankan semua procedure untuk update summary"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        logger.info("Menjalankan procedure update summary...")
        
        # Jalankan 3 procedure
        procedures = [
            'sp_update_summary_user_belanja',
            'sp_update_summary_pendapatan',
            'sp_update_summary_top_users'
        ]
        
        for proc_name in procedures:
            logger.info(f"  -> Jalankan {proc_name}()...")
            cursor.callproc(proc_name)
        
        conn.commit()
        logger.info("✓ Semua procedure berhasil dijalankan")
        
    except mysql.connector.Error as err:
        logger.error(f"Error menjalankan procedure: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# FUNGSI EXPORT KE CSV
# ============================================================================
def export_query_to_csv(query_name, query):
    """Export hasil query ke file CSV"""
    conn = get_db_connection()
    
    try:
        # Gunakan pandas untuk baca query langsung ke DataFrame
        df = pd.read_sql(query, conn)
        
        # Buat nama file dengan timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{query_name}_{timestamp}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Export ke CSV
        df.to_csv(filepath, index=False, encoding='utf-8')
        logger.info(f"✓ Export CSV: {filename} ({len(df)} baris)")
        
        return filepath
        
    except Exception as err:
        logger.error(f"Error export {query_name}: {err}")
    finally:
        conn.close()

# ============================================================================
# QUERY UNTUK EXPORT
# ============================================================================
QUERIES = {
    'user_belanja_lunas': """
        SELECT u.id, u.nama, u.email,
               COALESCE(SUM(p.total_harga), 0) AS total_belanja,
               COUNT(p.id) AS jumlah_pesanan,
               MAX(p.tanggal_pesan) AS terakhir_pesanan
        FROM users u
        LEFT JOIN pesanan p ON p.user_id = u.id AND p.status = 'lunas'
        GROUP BY u.id, u.nama, u.email
        HAVING SUM(p.total_harga) > 0
        ORDER BY total_belanja DESC;
    """,
    
    'pendapatan_bulanan_2026': """
        SELECT
          DATE_FORMAT(p.tanggal_pesan, '%Y-%m') AS tahun_bulan,
          MONTH(p.tanggal_pesan) AS bulan,
          DATE_FORMAT(p.tanggal_pesan, '%M') AS nama_bulan,
          SUM(p.total_harga) AS total_pendapatan,
          COUNT(p.id) AS jumlah_pesanan,
          SUM(SUM(p.total_harga)) OVER (ORDER BY DATE_FORMAT(p.tanggal_pesan, '%Y-%m')) AS pendapatan_kumulatif
        FROM pesanan p
        WHERE p.status = 'lunas' AND YEAR(p.tanggal_pesan) = 2026
        GROUP BY DATE_FORMAT(p.tanggal_pesan, '%Y-%m')
        ORDER BY tahun_bulan;
    """,
    
    'top_5_users': """
        SELECT u.id, u.nama, u.email,
               COUNT(p.id) AS jumlah_pesanan,
               SUM(CASE WHEN p.status = 'lunas' THEN p.total_harga ELSE 0 END) AS total_belanja_lunas,
               AVG(p.total_harga) AS rata2_per_pesanan,
               MAX(p.tanggal_pesan) AS terakhir_pesanan
        FROM users u
        JOIN pesanan p ON p.user_id = u.id
        GROUP BY u.id, u.nama, u.email
        ORDER BY jumlah_pesanan DESC, total_belanja_lunas DESC
        LIMIT 5;
    """
}

# ============================================================================
# FUNGSI MAIN UNTUK RUN SEMUA
# ============================================================================
def main():
    """Fungsi utama: update procedure & export ke CSV"""
    logger.info("=" * 70)
    logger.info(f"MULAI AUTO-UPDATE & EXPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # Step 1: Update procedure
    run_update_procedures()
    
    # Step 2: Export query ke CSV
    logger.info("\nMengexport query ke CSV...")
    for query_name, query_sql in QUERIES.items():
        export_query_to_csv(query_name, query_sql)
    
    # Step 3: Hapus file CSV lama (lebih dari 30 hari)
    logger.info("\nMenghapus file CSV lama (>30 hari)...")
    try:
        from pathlib import Path
        cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30 hari lalu
        deleted_count = 0
        
        for file in Path(OUTPUT_DIR).glob('*.csv'):
            if os.path.getmtime(file) < cutoff_time:
                os.remove(file)
                deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"✓ Hapus {deleted_count} file CSV lama")
    except Exception as err:
        logger.warning(f"Gagal hapus file lama: {err}")
    
    logger.info("=" * 70)
    logger.info("SELESAI")
    logger.info("=" * 70)

# ============================================================================
# FUNGSI UNTUK JALANKAN BERKALA (DAEMON MODE)
# ============================================================================
def run_daemon(interval_minutes=60):
    """Jalankan update berkala dalam mode daemon"""
    logger.info(f"Mode DAEMON: Update setiap {interval_minutes} menit")
    
    while True:
        try:
            main()
        except Exception as err:
            logger.error(f"Error di daemon: {err}")
        
        logger.info(f"Tunggu {interval_minutes} menit sebelum update berikutnya...")
        time.sleep(interval_minutes * 60)

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-update query & export CSV')
    parser.add_argument('--daemon', action='store_true', help='Jalankan dalam mode daemon (background)')
    parser.add_argument('--interval', type=int, default=60, help='Interval update dalam menit (default: 60)')
    
    args = parser.parse_args()
    
    try:
        if args.daemon:
            run_daemon(args.interval)
        else:
            main()
    except KeyboardInterrupt:
        logger.info("Dihentikan oleh user")
        sys.exit(0)
