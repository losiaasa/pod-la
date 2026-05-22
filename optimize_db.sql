-- ============================================================================
-- OPTIMASI DATABASE & AUTO-UPDATE BERKALA
-- ============================================================================

-- 1. TAMBAH INDEX UNTUK PERFORMA QUERY
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_pesanan_user_id ON pesanan(user_id);
CREATE INDEX IF NOT EXISTS idx_pesanan_status ON pesanan(status);
CREATE INDEX IF NOT EXISTS idx_pesanan_tanggal_pesan ON pesanan(tanggal_pesan);
CREATE INDEX IF NOT EXISTS idx_pesanan_user_status ON pesanan(user_id, status);

-- 2. BUAT TABEL UNTUK MENYIMPAN HASIL SUMMARY (auto-update berkala)
-- ============================================================================
CREATE TABLE IF NOT EXISTS summary_pendapatan_bulanan (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tahun_bulan VARCHAR(7) NOT NULL UNIQUE,
    bulan INT NOT NULL,
    nama_bulan VARCHAR(20),
    total_pendapatan DECIMAL(15, 2) DEFAULT 0,
    jumlah_pesanan INT DEFAULT 0,
    pendapatan_kumulatif DECIMAL(15, 2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS summary_top_users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    nama VARCHAR(255),
    email VARCHAR(255),
    jumlah_pesanan INT DEFAULT 0,
    total_belanja_lunas DECIMAL(15, 2) DEFAULT 0,
    rata2_per_pesanan DECIMAL(15, 2) DEFAULT 0,
    terakhir_pesanan DATETIME,
    ranking INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user (user_id)
);

CREATE TABLE IF NOT EXISTS summary_user_belanja (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    nama VARCHAR(255),
    email VARCHAR(255),
    total_belanja DECIMAL(15, 2) DEFAULT 0,
    jumlah_pesanan INT DEFAULT 0,
    terakhir_pesanan DATETIME,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user (user_id)
);

-- 3. BUAT PROCEDURE UNTUK UPDATE SUMMARY OTOMATIS
-- ============================================================================

-- Procedure untuk update summary belanja user
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS sp_update_summary_user_belanja()
BEGIN
    TRUNCATE TABLE summary_user_belanja;
    
    INSERT INTO summary_user_belanja (user_id, nama, email, total_belanja, jumlah_pesanan, terakhir_pesanan)
    SELECT u.id,
           u.nama,
           u.email,
           COALESCE(SUM(p.total_harga), 0) AS total_belanja,
           COUNT(p.id) AS jumlah_pesanan,
           MAX(p.tanggal_pesan) AS terakhir_pesanan
    FROM users u
    LEFT JOIN pesanan p ON p.user_id = u.id AND p.status = 'lunas'
    GROUP BY u.id, u.nama, u.email
    HAVING SUM(p.total_harga) > 0
    ORDER BY total_belanja DESC;
END //
DELIMITER ;

-- Procedure untuk update summary pendapatan bulanan
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS sp_update_summary_pendapatan()
BEGIN
    TRUNCATE TABLE summary_pendapatan_bulanan;
    
    INSERT INTO summary_pendapatan_bulanan (tahun_bulan, bulan, nama_bulan, total_pendapatan, jumlah_pesanan, pendapatan_kumulatif)
    SELECT
        DATE_FORMAT(p.tanggal_pesan, '%Y-%m') AS tahun_bulan,
        MONTH(p.tanggal_pesan) AS bulan,
        DATE_FORMAT(p.tanggal_pesan, '%M') AS nama_bulan,
        SUM(p.total_harga) AS total_pendapatan,
        COUNT(p.id) AS jumlah_pesanan,
        SUM(SUM(p.total_harga)) OVER (ORDER BY DATE_FORMAT(p.tanggal_pesan, '%Y-%m')) AS pendapatan_kumulatif
    FROM pesanan p
    WHERE p.status = 'lunas' AND YEAR(p.tanggal_pesan) = YEAR(CURDATE())
    GROUP BY DATE_FORMAT(p.tanggal_pesan, '%Y-%m'), MONTH(p.tanggal_pesan)
    ORDER BY tahun_bulan;
END //
DELIMITER ;

-- Procedure untuk update summary top users
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS sp_update_summary_top_users()
BEGIN
    TRUNCATE TABLE summary_top_users;
    
    INSERT INTO summary_top_users (user_id, nama, email, jumlah_pesanan, total_belanja_lunas, rata2_per_pesanan, terakhir_pesanan, ranking)
    SELECT u.id,
           u.nama,
           u.email,
           COUNT(p.id) AS jumlah_pesanan,
           SUM(CASE WHEN p.status = 'lunas' THEN p.total_harga ELSE 0 END) AS total_belanja_lunas,
           AVG(p.total_harga) AS rata2_per_pesanan,
           MAX(p.tanggal_pesan) AS terakhir_pesanan,
           ROW_NUMBER() OVER (ORDER BY COUNT(p.id) DESC, SUM(CASE WHEN p.status = 'lunas' THEN p.total_harga ELSE 0 END) DESC) AS ranking
    FROM users u
    JOIN pesanan p ON p.user_id = u.id
    GROUP BY u.id, u.nama, u.email
    ORDER BY jumlah_pesanan DESC, total_belanja_lunas DESC
    LIMIT 5;
END //
DELIMITER ;

-- 4. JALANKAN PROCEDURE SEKALI UNTUK ISI DATA AWAL
-- ============================================================================
CALL sp_update_summary_user_belanja();
CALL sp_update_summary_pendapatan();
CALL sp_update_summary_top_users();

-- 5. VERIFIKASI DATA SUMMARY
-- ============================================================================
-- Lihat hasil summary user belanja
SELECT '=== SUMMARY USER BELANJA ===' AS info;
SELECT * FROM summary_user_belanja ORDER BY total_belanja DESC;

-- Lihat hasil summary pendapatan bulanan
SELECT '=== SUMMARY PENDAPATAN BULANAN ===' AS info;
SELECT * FROM summary_pendapatan_bulanan ORDER BY tahun_bulan;

-- Lihat hasil summary top 5 users
SELECT '=== SUMMARY TOP 5 USERS ===' AS info;
SELECT * FROM summary_top_users ORDER BY ranking;

-- ============================================================================
-- UNTUK AUTO-UPDATE BERKALA (CRON JOB via OS atau Event Scheduler MySQL)
-- ============================================================================
-- Opsi 1: Gunakan MySQL Event Scheduler (auto-update setiap jam)
-- 
-- CALL sp_update_summary_user_belanja();
-- CALL sp_update_summary_pendapatan();
-- CALL sp_update_summary_top_users();
-- 
-- Opsi 2: Gunakan cron job di Linux/macOS (jalankan setiap jam)
-- 0 * * * * mysql -u root -p latihan_db -e "CALL sp_update_summary_user_belanja(); CALL sp_update_summary_pendapatan(); CALL sp_update_summary_top_users();"
--
-- Opsi 3: Atau buat Python/Node script yang jalankan procedure berkala
-- ============================================================================
