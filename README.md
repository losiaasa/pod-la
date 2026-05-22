# Setup Auto-Update Database & Export Query ke CSV

Dokumentasi lengkap untuk menjalankan query otomatis berkala dan menyimpan hasil ke CSV.

---

## 📋 File yang Dibuat

1. **optimize_db.sql** — Script SQL untuk:
   - Tambah INDEX untuk performa query
   - Buat tabel summary (hasil query yang disimpan)
   - Buat PROCEDURE untuk auto-update summary

2. **auto_update.py** — Script Python untuk:
   - Jalankan procedure MySQL secara berkala
   - Export hasil query ke file CSV
   - Hapus file lama (>30 hari)
   - Mode daemon (background service)

3. **setup_cron.sh** — Setup automated cron job (optional)

4. **README.md** — Dokumentasi ini

---

## 🚀 Langkah-Langkah Setup

### 1. Jalankan Script SQL di MySQL

```bash
# Masuk ke direktori file
cd /home/kayto/rui

# Jalankan file SQL (masukkan password ketika diminta)
mysql -u root -p latihan_db < optimize_db.sql
```

Output yang diharapkan:
- Query berhasil, melihat hasil summary di 3 tabel baru
- Jika ada error, periksa nama kolom/tabel sesuai skema Anda

---

### 2. Persiapan Python Script

#### 2a. Install dependencies (jika belum ada)

```bash
# Jika menggunakan pip
pip install mysql-connector-python pandas

# Atau jika menggunakan conda
conda install -c conda-forge mysql-connector-python pandas
```

#### 2b. Edit konfigurasi di `auto_update.py`

Buka file dan sesuaikan kredensial:

```python
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',                    # ← Sesuaikan username
    'password': 'rahasia123',          # ← Sesuaikan password
    'database': 'latihan_db'           # ← Sesuaikan nama database
}

OUTPUT_DIR = '/home/kayto/rui/query_results'  # ← Folder output CSV
```

#### 2c. Buat folder output jika belum ada

```bash
mkdir -p /home/kayto/rui/query_results
```

---

### 3. Jalankan Script Python

#### Opsi A: Jalankan Sekali (Manual)

```bash
# Jalankan sekali sekarang
python3 /home/kayto/rui/auto_update.py
```

Ekspektasi output:
- Log di console
- File CSV dibuat di `/home/kayto/rui/query_results/`
- Log juga disimpan di `/home/kayto/rui/auto_update.log`

#### Opsi B: Jalankan Berkala (Background Daemon)

Jalankan dalam mode daemon (auto-update setiap jam):

```bash
# Mode daemon - update setiap 60 menit
python3 /home/kayto/rui/auto_update.py --daemon --interval 60

# Atau update setiap 30 menit
python3 /home/kayto/rui/auto_update.py --daemon --interval 30
```

Untuk background (jangan terganggu terminal):

```bash
nohup python3 /home/kayto/rui/auto_update.py --daemon --interval 60 > /home/kayto/rui/daemon.log 2>&1 &
```

---

### 4. Setup Cron Job (Auto-Update Berkala)

#### Opsi A: Cron Job Linux/macOS

Edit crontab:

```bash
crontab -e
```

Tambahkan baris berikut (sesuaikan path):

```bash
# Update setiap jam di menit 0 (00:00, 01:00, 02:00, ...)
0 * * * * python3 /home/kayto/rui/auto_update.py >> /home/kayto/rui/cron.log 2>&1

# Atau update setiap 30 menit
*/30 * * * * python3 /home/kayto/rui/auto_update.py >> /home/kayto/rui/cron.log 2>&1

# Atau update setiap hari jam 23:00 (11 malam)
0 23 * * * python3 /home/kayto/rui/auto_update.py >> /home/kayto/rui/cron.log 2>&1
```

#### Opsi B: MySQL Event Scheduler (Di dalam MySQL)

Jika ingin auto-update hanya dari database (tanpa Python):

```sql
-- Aktifkan Event Scheduler
SET GLOBAL event_scheduler = ON;

-- Buat Event untuk jalankan procedure setiap jam
CREATE EVENT IF NOT EXISTS event_update_summary_hourly
ON SCHEDULE EVERY 1 HOUR
DO
BEGIN
    CALL sp_update_summary_user_belanja();
    CALL sp_update_summary_pendapatan();
    CALL sp_update_summary_top_users();
END;

-- Verifikasi event sudah berjalan
SHOW EVENTS;
```

---

## 📊 Hasil Output

Setelah script jalan, Anda akan punya:

### 1. File CSV di `/home/kayto/rui/query_results/`

```
user_belanja_lunas_20260522_143025.csv
pendapatan_bulanan_2026_20260522_143025.csv
top_5_users_20260522_143025.csv
```

### 2. Tabel Summary di Database

Buka database client dan cek:

```sql
SELECT * FROM summary_user_belanja;
SELECT * FROM summary_pendapatan_bulanan;
SELECT * FROM summary_top_users;
```

### 3. Log File

- **Console**: Lihat di terminal
- **File**: `/home/kayto/rui/auto_update.log` (permanent)
- **Cron**: `/home/kayto/rui/cron.log` (jika pakai cron)

---

## 🔍 Troubleshooting

### Error: `mysql.connector.Error: 2003 (HY000): Can't connect to MySQL server`

**Solusi:**
- Pastikan MySQL running: `sudo systemctl start mysql`
- Cek host/port/user/password di `DB_CONFIG`
- Gunakan `127.0.0.1` jika localhost tidak bekerja

### Error: `ModuleNotFoundError: No module named 'mysql'`

**Solusi:**
```bash
pip install mysql-connector-python
```

### Error: `Access denied for user 'root'@'127.0.0.1'`

**Solusi:**
- Periksa password di `DB_CONFIG`
- Atau test koneksi manual: `mysql -u root -p -h 127.0.0.1`

### File CSV tidak terbuat / Procedure gagal

**Solusi:**
- Pastikan sudah jalankan `optimize_db.sql` terlebih dahulu
- Cek struktur tabel: `DESCRIBE users;` dan `DESCRIBE pesanan;`
- Lihat log di `/home/kayto/rui/auto_update.log` untuk error detail

---

## ⚙️ Customization

### Edit Interval Auto-Update

Buka `auto_update.py` dan ubah:

```python
def run_daemon(interval_minutes=60):  # Ubah 60 ke nilai lain (dalam menit)
```

### Edit Query yang Diexport

Buka `auto_update.py` dan modifikasi dictionary `QUERIES`:

```python
QUERIES = {
    'nama_query': """SELECT ... FROM ...;""",
    # Tambah query baru di sini
}
```

### Tambah Notifikasi Email

Saat auto-update selesai, kirim email:

```python
import smtplib
from email.mime.text import MIMEText

def send_email_notification():
    # Kode untuk kirim email
    pass
```

---

## 📝 Tips

1. **Backup database secara berkala:**
   ```bash
   mysqldump -u root -p latihan_db > backup_$(date +%Y%m%d).sql
   ```

2. **Monitor cron job:**
   ```bash
   tail -f /home/kayto/rui/cron.log
   ```

3. **Stop daemon:**
   ```bash
   pkill -f "python3 /home/kayto/rui/auto_update.py"
   ```

4. **Cek ruang disk CSV:**
   ```bash
   du -sh /home/kayto/rui/query_results/
   ```

---

## 📞 Support

Jika ada pertanyaan atau error:
1. Cek log file di `/home/kayto/rui/auto_update.log`
2. Verifikasi struktur database: `SHOW TABLES;`
3. Test koneksi: `mysql -u root -p -h 127.0.0.1 latihan_db`

---

**Last Updated:** 22 Mei 2026
