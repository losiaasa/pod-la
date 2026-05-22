services:
  # Ini container mysql kagu yang sudan ada sebelumnya
  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    # ... settingan mysql lainnya ...

  # 👇 CARA NAMBAH CONTAINER BARU (Contoh: Aplikasi Go Baru)
  server-go-baru:
    build:
      context: ./folder-go-baru # Arahkan ke folder kode Go barumu
      dockerfile: Dockerfile
    ports:
      - "8081:8081" # Port aplikasi (Port_Luar:Port_Dalam_Container)
    environment:
      - DB_HOST=mysql # Bisa langsung panggil nama container mysql di atas
      - DB_USER=root
    depends_on:
      - mysql # Memastikan mysql jalan duluan sebelum container ini aktif