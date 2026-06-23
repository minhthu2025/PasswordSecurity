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

**Lưu ý quan trọng — hai MySQL khác nhau:**

| Cổng | Vị trí | Dùng khi nào |
|------|--------|--------------|
| `localhost:3306` | MySQL trên máy host | Đăng ký/đăng nhập khi chạy `streamlit run app.py` local |
| `localhost:3307` | MySQL trong Docker (`passwordsecurity-db`) | Đăng nhập qua Streamlit Docker (`http://localhost:8501`) |

Hai DB **độc lập**. Nếu chỉ có dữ liệu trên host:3306 mà chạy Docker thuần (`docker compose up`) sẽ báo **"Tài khoản không tồn tại"**.

---

## Cách 1 — Docker: Giao diện web Streamlit (khuyến nghị)

Stack gồm 3 service: `db` (MySQL), `migrate` (đồng bộ dữ liệu), `app` (Streamlit).

### Khởi động có tự động migrate host → Docker (khuyến nghị)

Dùng script wrapper — export MySQL host (`3306`) rồi import vào DB Docker (`3307`):

```bash
# Lần đầu hoặc sau khi đổi Dockerfile/requirements.txt
bash scripts/docker_compose_up.sh --build

# Chạy nền (detached)
bash scripts/docker_compose_up.sh -d --build
```

Script thực hiện (3 bước):
1. `scripts/export_host_mysql.sh` → tạo `docker-migrate/seed.sql`
2. Khởi động `db` trước, **chờ MySQL healthy** (lần đầu có thể 2–10 phút), tự reset volume nếu init bị kill/OOM
3. Build (nếu có `--build`) rồi chạy `migrate` → import seed → `app` (Streamlit)

> **Lưu ý:** Luôn dùng `scripts/docker_compose_up.sh` thay cho `docker compose up` trực tiếp — tránh lỗi `db is unhealthy` khi build image song song với MySQL init lần đầu.

Truy cập: **http://localhost:8501**

MySQL Docker (từ máy host): `localhost:3307` — user `root`, password theo `DB_PASSWORD` trong `.env`.

### Khởi động Docker không migrate (chỉ dùng DB Docker hiện có)

Tắt migrate trong `.env`: `AUTO_MIGRATE_FROM_HOST=0`, rồi vẫn dùng script wrapper:

```bash
bash scripts/docker_compose_up.sh --build      # foreground
bash scripts/docker_compose_up.sh -d --build   # nền
```

Không khuyến nghị `docker compose up` trực tiếp — dễ gặp `db is unhealthy` trên Docker Desktop (macOS).

### Biến môi trường migrate (trong `.env`, tùy chọn)

```env
AUTO_MIGRATE_FROM_HOST=1          # 1 = bật migrate khi up (mặc định)
MIGRATE_SOURCE_HOST=127.0.0.1
MIGRATE_SOURCE_PORT=3306
# MIGRATE_FORCE=1                # bật nếu muốn luôn ghi đè DB Docker từ host
```

- Migrate **chỉ chạy** khi DB Docker có **ít user hơn** DB host (trừ khi `MIGRATE_FORCE=1`).
- `MASTER_KEY` trong `.env` phải **trùng** với lúc mã hóa dữ liệu trên host (để đăng nhập bằng email).

### Export thủ công (không cần khởi động Docker)

```bash
bash scripts/export_host_mysql.sh
# Tạo: docker-migrate/seed.sql và docker-migrate/meta.env
```

Sau đó chạy `bash scripts/docker_compose_up.sh -d` — service `migrate` sẽ import file seed.

### Xử lý lỗi `db is unhealthy` / MySQL init bị OOM

```bash
# Reset volume Docker (không ảnh hưởng MySQL host:3306) rồi chạy lại
docker compose down -v
bash scripts/docker_compose_up.sh --build
```

Nếu vẫn lỗi do Docker Desktop thiếu RAM (Settings → Resources → Memory ≥ 6GB), dùng MySQL trên máy thay container:

```bash
DOCKER_USE_HOST_DB=1 bash scripts/docker_compose_up.sh --build
# App kết nối host.docker.internal:3306, bỏ qua db/migrate
```

---

## Cách 2 — Docker: CLI tương tác (`main.py`)

Ghi đè lệnh mặc định để vào menu dòng lệnh:

```bash
# 1. Khởi động stack nền (db + migrate + app)
bash scripts/docker_compose_up.sh -d --build

# 2. Chạy CLI (menu đầy đủ, gõ phím bình thường)
docker compose run --rm -it app python main.py
```

Một lệnh (stack nền + vào luôn CLI):

```bash
bash scripts/docker_compose_up.sh -d --build && docker compose run --rm -it app python main.py
```

---

## Các lệnh hay dùng

```bash
# Dừng toàn bộ stack
docker compose down

# Dừng và xóa volume database Docker (mất dữ liệu trong container, KHÔNG ảnh hưởng MySQL host:3306)
docker compose down -v

# Xem log migrate (đồng bộ host → Docker)
docker compose logs migrate

# Xem log ứng dụng web
docker compose logs -f app

# Xem log database
docker compose logs -f db

# Khởi động lại chỉ service app (không chạy lại migrate)
docker compose restart app

# Chạy lại migrate thủ công (sau khi export seed mới)
bash scripts/export_host_mysql.sh
docker compose run --rm migrate

# Vào shell trong container app (debug)
docker compose run --rm -it app bash
```

### Kiểm tra nhanh sau migrate

```bash
# Số user trong DB Docker
mysql -h 127.0.0.1 -P 3307 -uroot -p"$DB_PASSWORD" \
  -e "SELECT COUNT(*) AS users FROM password_security.users;"

# Số user trong DB host
mysql -h 127.0.0.1 -P 3306 -uroot -p"$DB_PASSWORD" \
  -e "SELECT COUNT(*) AS users FROM password_security.users;"
```

---

## Chạy thủ công (không Docker)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Chỉnh DB_HOST=localhost, DB_PASSWORD, MASTER_KEY

# Terminal 1: MySQL host đang chạy trên port 3306
# (hoặc chỉ DB Docker: docker compose up -d db, rồi đổi DB_HOST=localhost DB_PORT=3307)

streamlit run app.py    # Giao diện web → http://localhost:8501
python main.py          # Giao diện CLI
```

Kiểm tra & demo:

```bash
python test_bulk_passwords.py
python demo_weaknesses.py
```