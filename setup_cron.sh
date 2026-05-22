#!/bin/bash
# ============================================================================
# Setup Cron Job untuk Auto-Update Database Query
# ============================================================================

set -e

SCRIPT_DIR="/home/kayto/rui"
SCRIPT_PATH="$SCRIPT_DIR/auto_update.py"
LOG_PATH="$SCRIPT_DIR/cron.log"

echo "🔧 Setup Cron Job untuk Auto-Update Database"
echo "=============================================="

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

# Check if Python installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 tidak ditemukan"
    exit 1
fi

# Tanya user untuk interval
echo ""
echo "Berapa menit interval untuk auto-update?"
echo "1) Setiap 30 menit"
echo "2) Setiap 60 menit (default)"
echo "3) Setiap 4 jam"
echo "4) Setiap hari (jam 23:00)"
echo "5) Custom (masukkan manual)"
read -p "Pilih [1-5]: " interval_choice

case $interval_choice in
    1)
        CRON_SCHEDULE="*/30 * * * *"
        DESC="setiap 30 menit"
        ;;
    2)
        CRON_SCHEDULE="0 * * * *"
        DESC="setiap jam"
        ;;
    3)
        CRON_SCHEDULE="0 */4 * * *"
        DESC="setiap 4 jam"
        ;;
    4)
        CRON_SCHEDULE="0 23 * * *"
        DESC="setiap hari jam 23:00"
        ;;
    5)
        read -p "Masukkan cron schedule (misal: 0 */6 * * *): " CRON_SCHEDULE
        DESC="dengan schedule: $CRON_SCHEDULE"
        ;;
    *)
        echo "❌ Pilihan tidak valid"
        exit 1
        ;;
esac

# Buat cron command
CRON_CMD="$CRON_SCHEDULE python3 $SCRIPT_PATH >> $LOG_PATH 2>&1"

echo ""
echo "📋 Cron yang akan ditambahkan:"
echo "   Schedule: $DESC"
echo "   Command:  $CRON_CMD"
echo ""

read -p "Lanjutkan? [y/n]: " confirm

if [ "$confirm" != "y" ]; then
    echo "❌ Dibatalkan"
    exit 0
fi

# Backup crontab existing
BACKUP_CRONTAB="/tmp/crontab_backup_$(date +%Y%m%d_%H%M%S)"
crontab -l > "$BACKUP_CRONTAB" 2>/dev/null || true

echo ""
echo "💾 Backup crontab: $BACKUP_CRONTAB"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$SCRIPT_PATH"; then
    echo ""
    echo "⚠️  Cron job untuk script ini sudah ada"
    read -p "Ganti? [y/n]: " replace_confirm
    
    if [ "$replace_confirm" = "y" ]; then
        # Remove old cron
        (crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH"; echo "$CRON_CMD") | crontab - 
        echo "✅ Cron job diupdate"
    else
        echo "❌ Dibatalkan"
        exit 0
    fi
else
    # Add new cron job
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✅ Cron job ditambahkan"
fi

# Verifikasi
echo ""
echo "📍 Verifikasi cron job yang aktif:"
crontab -l 2>/dev/null | grep "$SCRIPT_PATH"

echo ""
echo "✅ Setup selesai!"
echo ""
echo "📌 Tips:"
echo "   • Lihat log: tail -f $LOG_PATH"
echo "   • Edit cron: crontab -e"
echo "   • Hapus cron: crontab -r"
echo "   • Restore backup: crontab $BACKUP_CRONTAB"
echo ""
