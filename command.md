# Command chạy chuẩn (copy paste dùng luôn)

## Chuẩn bị (lần đầu)

```bash
cp .env.example .env
# Chỉnh DB_PASSWORD và MASTER_KEY trong .env
```

Tạo `MASTER_KEY` mới (32 byte hex):

```bash
python -c "import os; print(os.urandom(32).hex())"
```

---

## Cách 1 — Docker: Giao diện web Streamlit (khuyến nghị)

Container `app` mặc định chạy `streamlit run app.py` (xem `Dockerfile`).

```bash
# Build image (lần đầu hoặc sau khi thay đổi Dockerfile/requirements.txt)
docker compose build

# Khởi động toàn bộ (MySQL + PassGuard web)
docker compose up --build
```

Chạy nền (detached):

```bash
docker compose up -d --build
```

Truy cập: **http://localhost:8501**

MySQL (từ máy host): `localhost:3307` — user `root`, password theo `DB_PASSWORD` trong `.env`.

---

## Cách 2 — Docker: CLI tương tác (`main.py`)

Ghi đè lệnh mặc định để vào menu dòng lệnh:

```bash
# 1. Khởi động database chạy nền
docker compose up -d db

# 2. Chạy CLI (menu đầy đủ, gõ phím bình thường)
docker compose run --rm -it app python main.py
```

Một lệnh (db nền + vào luôn CLI):

```bash
docker compose up -d db && docker compose run --rm -it app python main.py
```

---

## Các lệnh hay dùng

```bash
# Dừng toàn bộ stack
docker compose down

# Dừng và xóa volume database (mất dữ liệu đã lưu)
docker compose down -v

# Xem log ứng dụng web
docker compose logs -f app

# Xem log database
docker compose logs -f db

# Khởi động lại chỉ service app
docker compose restart app

# Vào shell trong container app (debug)
docker compose run --rm -it app bash
```

---

## Chạy thủ công (không Docker)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Chỉnh DB_HOST=localhost, DB_PASSWORD, MASTER_KEY

# Terminal 1: MySQL đang chạy (hoặc chỉ db: docker compose up -d db)

streamlit run app.py    # Giao diện web → http://localhost:8501
python main.py          # Giao diện CLI
```

Kiểm tra & demo:

```bash
python test_bulk_passwords.py
python demo_weaknesses.py
```
