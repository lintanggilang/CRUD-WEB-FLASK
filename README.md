# Flask Async Web Application

## Instalasi

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Jalankan aplikasi:
```bash
python run.py
```

## Akses Aplikasi

- URL: http://127.0.0.1:5000
- Default Admin: username=`admin`, password=`admin`

## Fitur

### Admin:
- Login dan dashboard admin
- CRUD data pada tabel
- Tambah user baru dengan permission city
- Manajemen akses berdasarkan city

### User:
- Login dan dashboard user  
- View data read-only
- Akses terbatas sesuai permission city

## Struktur Database

- `users`: id, username, password_hash, role
- `permissions`: id, user_id, city  
- `data_table`: id, city, data_field1, data_field2

## Bonus (runapp.bat)

@echo off
cd /d D:\path\ke\folder_project
call venv\Scripts\activate
start "" python run.py
timeout /t 3 >nul
start "" http://127.0.0.1:5000/