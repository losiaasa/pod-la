-- ============================================================================
-- SETUP MYSQL EVENT SCHEDULER (Alternatif cron job - auto-update di database)
-- ============================================================================
-- Jalankan script ini jika ingin auto-update hanya dari dalam MySQL
-- tanpa perlu Python/cron job Linux

-- 1. AKTIFKAN EVENT SCHEDULER
-- ============================================================================
SET GLOBAL event_scheduler = ON;

-- Verifikasi status
SHOW VARIABLES LIKE 'event_scheduler';

-- 2. BUAT EVENT UNTUK AUTO-UPDATE SETIAP JAM
-- ============================================================================
CREATE EVENT IF NOT EXISTS event_update_summary_hourly
ON SCHEDULE EVERY 1 HOUR
STARTS CURRENT_TIMESTAMP
ON COMPLETION PRESERVE
ENABLE
DO
BEGIN
    -- Jalankan 3 procedure untuk update summary
    CALL sp_update_summary_user_belanja();
    CALL sp_update_summary_pendapatan();
    CALL sp_update_summary_top_users();
    
    -- Log info
    INSERT INTO event_log (event_name, executed_at, status)
    VALUES ('update_summary_hourly', NOW(), 'SUCCESS');
END //

-- 3. BUAT EVENT UNTUK AUTO-UPDATE SETIAP 30 MENIT (OPTIONAL)
-- ============================================================================
-- CREATE EVENT IF NOT EXISTS event_update_summary_30min
-- ON SCHEDULE EVERY 30 MINUTE
-- STARTS CURRENT_TIMESTAMP
-- ON COMPLETION PRESERVE
-- ENABLE
-- DO
-- BEGIN
--     CALL sp_update_summary_user_belanja();
--     CALL sp_update_summary_pendapatan();
--     CALL sp_update_summary_top_users();
-- END //

-- 4. BUAT TABEL UNTUK LOG EVENT (OPTIONAL - untuk tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS event_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    event_name VARCHAR(100),
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    error_message TEXT
);

-- 5. LIHAT SEMUA EVENT YANG AKTIF
-- ============================================================================
SHOW EVENTS;

-- 6. TIPS MANAGEMENT EVENT
-- ============================================================================
-- Disable event:
-- ALTER EVENT event_update_summary_hourly DISABLE;

-- Enable event:
-- ALTER EVENT event_update_summary_hourly ENABLE;

-- Drop event:
-- DROP EVENT IF EXISTS event_update_summary_hourly;

-- Disable/Enable event scheduler globally:
-- SET GLOBAL event_scheduler = OFF;
-- SET GLOBAL event_scheduler = ON;

-- Lihat log event:
-- SELECT * FROM event_log ORDER BY executed_at DESC;

-- ============================================================================
-- PERBANDINGAN: CRON vs EVENT SCHEDULER
-- ============================================================================
-- CRON JOB (Python + Linux):
--   ✓ Lebih flexible (bisa jalankan file eksternal, kirim email, etc)
--   ✓ Bisa run even jika MySQL down (tapi mungkin fail)
--   ✗ Tergantung Python & system
--
-- EVENT SCHEDULER (MySQL):
--   ✓ Langsung di database
--   ✓ Terintegrasi dengan MySQL
--   ✗ Hanya bisa jalankan SQL query
--   ✗ Tergantung MySQL harus on 24/7
--
-- Rekomendasi: Gunakan CRON (Python) untuk production, 
--              atau gunakan keduanya untuk redundancy
-- ============================================================================
