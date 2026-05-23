#!/bin/bash

# Script untuk UPDATE data MySQL dari terminal
# Penggunaan: ./update-data.sh

MYSQL_USER="root"
MYSQL_PASS="rootpassword"
MYSQL_DB="latihan_db"
CONTAINER="rui-db-1"

echo "=== UPDATE DATA MYSQL ==="
echo ""

# Update 1: Ubah nama user
echo "1. Ubah nama user (id=1) menjadi 'Budi Santoso':"
docker exec $CONTAINER mysql -u $MYSQL_USER -p$MYSQL_PASS $MYSQL_DB -e \
  "UPDATE users SET nama='Budi Santoso' WHERE id=1; SELECT * FROM users WHERE id=1;"

echo ""

# Update 2: Ubah email user
echo "2. Ubah email user (id=2) menjadi 'ani.wijaya@example.com':"
docker exec $CONTAINER mysql -u $MYSQL_USER -p$MYSQL_PASS $MYSQL_DB -e \
  "UPDATE users SET email='ani.wijaya@example.com' WHERE id=2; SELECT * FROM users WHERE id=2;"

echo ""

# Update 3: Ubah status pesanan ke 'lunas'
echo "3. Ubah status pesanan (id=2) menjadi 'lunas':"
docker exec $CONTAINER mysql -u $MYSQL_USER -p$MYSQL_PASS $MYSQL_DB -e \
  "UPDATE pesanan SET status='lunas' WHERE id=2; SELECT * FROM pesanan WHERE id=2;"

echo ""

# Update 4: Ubah total harga pesanan
echo "4. Ubah total harga pesanan (id=3) menjadi 250000:"
docker exec $CONTAINER mysql -u $MYSQL_USER -p$MYSQL_PASS $MYSQL_DB -e \
  "UPDATE pesanan SET total_harga=250000.00 WHERE id=3; SELECT * FROM pesanan WHERE id=3;"

echo ""
echo "=== CEK SEMUA DATA ==="
echo ""

echo "Data Users:"
docker exec $CONTAINER mysql -u $MYSQL_USER -p$MYSQL_PASS $MYSQL_DB -e "SELECT * FROM users;"

echo ""
echo "Data Pesanan:"
docker exec $CONTAINER mysql -u $MYSQL_USER -p$MYSQL_PASS $MYSQL_DB -e "SELECT * FROM pesanan;"
