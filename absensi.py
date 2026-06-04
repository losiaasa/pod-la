import time

# 1. Inisialisasi data karyawan awal (John Doe)
karyawan = {
    'name': 'John Doe',
    'email': 'john.doe@example.com',
    'age': 30,
    'total_work_hours': 0.0  # Mulai dari 0 detik/jam
}

print("=== SISTEM LOG WAKTU KERJA KARYAWAN ===")
print("Profil Saat Ini:")
print(f"Nama: {karyawan['name']}")
print(f"Email: {karyawan['email']}")
print(f"Total Jam Kerja Sebelumnya: {karyawan['total_work_hours']} detik\n")
print("-" * 45)

# 2. Proses Tracking Waktu Kerja (Timer)
# Tombol Start Shift
input("Press Enter untuk MEMULAI Shift Kerja (Clock In)...")
waktu_mulai = time.time()
jam_mulai = time.ctime(waktu_mulai)
print(f"Status: Shift Telah Dimulai.")
print("-" * 45)

# Tombol Stop Shift
input("Press Enter untuk MENGAKHIRI Shift Kerja (Clock Out)...")
waktu_selesai = time.time()
jam_selesai = time.ctime(waktu_selesai)
durasi_kerja = waktu_selesai - waktu_mulai

# Hitung konversi menit dan detik untuk tampilan log
menit = int(durasi_kerja // 60)
detik = int(durasi_kerja % 60)

print("-" * 45)

# Tampilan catatan teks ke bawah sesuai permintaanmu
print("[LOG AKTIVITAS KERJA]")
print(f"Aku kerja dari jam          : {jam_mulai}")
print(f"Aku berhenti kerja dari jam : {jam_selesai}")
print(f"Total durasi shift ini      : {menit} menit {detik} detik")
print("-" * 45)


# 3. Fungsi untuk menyatukan data lama dengan data durasi kerja yang baru
def update_jam_kerja(data_lama, durasi_baru, mulai, selesai):
    # Mengakumulasikan total jam kerja lama + durasi baru
    total_baru = round(data_lama['total_work_hours'] + durasi_baru, 2)
    
    # Data tambahan baru yang dimasukkan ke dictionary
    data_update = {
        'total_work_hours': total_baru,
        'log_jam_mulai': mulai,
        'log_jam_selesai': selesai
    }
    # Menggunakan fungsi .update()
    data_lama.update(data_update)
    return data_lama


# 4. Menjalankan fungsi update dan menampilkan hasil akhir
karyawan_updated = update_jam_kerja(karyawan, durasi_kerja, jam_mulai, jam_selesai)

print("\n=== DATA KARYAWAN TERBARU (SUDAH DI-UPDATE) ===")
print(karyawan_updated)
print("================================================")
