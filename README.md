# PassGuard — Công cụ Kiểm tra Độ Mạnh Mật Khẩu & Mã Hóa Dữ Liệu

**Đề tài 12** — Nhóm Mã hóa và Thám mã  
Môn: An toàn thông tin

---

## 1. Mục tiêu

Bài toán đặt ra: người dùng thường đặt mật khẩu yếu, dễ đoán hoặc lưu trữ mật khẩu không an toàn (plaintext, MD5 không salt). Kẻ tấn công có thể dùng **Rainbow Table** để tra cứu hash và phục hồi mật khẩu gốc trong vài giây.

Dự án giải quyết 3 vấn đề cốt lõi:

| Vấn đề | Giải pháp |
|--------|-----------|
| Mật khẩu yếu, không có tiêu chí đánh giá | Module kiểm tra độ mạnh theo thời gian thực |
| Hash mật khẩu không an toàn (MD5, SHA-1 không salt) | Argon2id + Salt ngẫu nhiên (memory-hard) |
| Dữ liệu cá nhân lưu plaintext trong CSDL | Mã hóa AES-256-GCM tại rest |

---

## 2. Cơ sở lý thuyết

### 2.1 Argon2id — Hàm băm mật khẩu chuyên dụng

Argon2 là thuật toán băm mật khẩu đoạt giải Password Hashing Competition (2015). Biến thể **Argon2id** kết hợp Argon2i (chống side-channel) và Argon2d (chống GPU/ASIC).

**Toán học đằng sau:**

```
output = Argon2id(password, salt, t, m, p, taglen)
```

- `t` (time_cost): số vòng lặp — tăng CPU time
- `m` (memory_cost): RAM tối thiểu phải dùng (KB) — chống GPU/ASIC vì VRAM đắt
- `p` (parallelism): số luồng song song

Cấu hình dự án (`memory=100MiB, t=2, p=8`) đảm bảo mỗi lần hash tốn ~100MB RAM và ~vài trăm ms — quá chậm để brute-force hàng loạt.

**Salt ngẫu nhiên** (16 byte) được sinh tự động mỗi lần hash → cùng mật khẩu cho ra hash khác nhau → vô hiệu hóa Rainbow Table.

**So sánh với MD5/SHA không salt:**
```
MD5("password") = 5f4dcc3b5aa765d61d8327deb882cf99  ← tra bảng ngay
Argon2id("password", salt=random) = $argon2id$v=19$...  ← không tra được
```

### 2.2 AES-256-GCM — Mã hóa dữ liệu cá nhân

**AES (Advanced Encryption Standard)** là block cipher hoạt động trên khối 128-bit với khóa 256-bit (14 vòng).

**Chế độ GCM (Galois/Counter Mode):**
```
Ciphertext = AES_CTR(plaintext, key, IV)
AuthTag    = GHASH(AAD || Ciphertext)
```

- **IV ngẫu nhiên 12 byte** mỗi lần mã hóa → cùng dữ liệu cho ciphertext khác nhau
- **AuthTag 16 byte** xác thực tính toàn vẹn — phát hiện nếu dữ liệu bị giả mạo
- **Điểm yếu nếu dùng sai**: AES-ECB (không IV) → plaintext giống nhau → ciphertext giống nhau → lộ pattern (xem `demo_weaknesses.py` Demo 2)

### 2.3 Chính sách mật khẩu

| Mức | Tiêu chí |
|-----|----------|
| Yếu | Dưới 8 ký tự hoặc thiếu điều kiện bắt buộc |
| Trung bình | Đủ điều kiện, 8–11 ký tự |
| Mạnh | Đủ điều kiện, ≥ 12 ký tự |

Điều kiện bắt buộc: chữ hoa + chữ thường + số + ký tự đặc biệt.

---

## 3. Kịch bản thực nghiệm

### Kịch bản 1 — Rainbow Table Attack
Chạy `demo_weaknesses.py` (Demo 1): hash cùng mật khẩu bằng MD5 không salt → tra bảng crack ngay lập tức. Hash bằng Argon2id + salt → không tra được.

### Kịch bản 2 — AES-ECB vs AES-GCM
Chạy `demo_weaknesses.py` (Demo 2): mã hóa dữ liệu lặp lại bằng ECB → ciphertext lặp lại, lộ pattern. GCM với IV ngẫu nhiên → ciphertext hoàn toàn khác nhau.

### Kịch bản 3 — Benchmark Argon2 memory-hard
Chạy `demo_weaknesses.py` (Demo 3): đo thời gian hash theo memory_cost (8MB / 32MB / 64MB / 100MB) → chứng minh chi phí tính toán tăng tuyến tính, GPU brute-force không khả thi.

### Kịch bản 4 — Kiểm tra độ mạnh hàng loạt
Chạy `test_bulk_passwords.py`: đọc 25 mật khẩu mẫu từ `tests/test_passwords.txt`, phân loại Yếu/Trung bình/Mạnh, in bảng thống kê.

### Kịch bản 5 — Giao diện Web (Streamlit)
Chạy `streamlit run app.py`: đăng ký tài khoản, kiểm tra độ mạnh theo thời gian thực, đăng nhập, xem/cập nhật profile, đổi mật khẩu.

---

## 4. Kết quả đạt được

- **Module kiểm tra độ mạnh** hoạt động theo thời gian thực trên giao diện web
- **Đăng ký người dùng** với hash Argon2id + salt tự động — chống Rainbow Table
- **Mã hóa AES-256-GCM** toàn bộ PII (họ tên, email, SĐT, CMND, địa chỉ) trước khi lưu DB
- **Cơ chế chống brute-force**: khóa tài khoản 3 phút sau 5 lần đăng nhập sai
- **Demo trực quan** 4 điểm yếu bảo mật với kết quả đo đạc thực tế
- **Giao diện web PassGuard** (Streamlit) đầy đủ chức năng, chạy được trong Docker

---

## 5. Biện pháp phòng chống

| Mối đe dọa | Biện pháp trong dự án |
|------------|----------------------|
| Rainbow Table | Argon2id + Salt ngẫu nhiên 16 byte |
| Brute-force online | Lockout 5 lần / 3 phút |
| Brute-force offline (GPU) | Argon2id memory-hard 100MiB — GPU VRAM không đủ |
| Lộ CSDL | AES-256-GCM mã hóa toàn bộ PII, MASTER_KEY tách biệt |
| Mã hóa sai chế độ (ECB) | Dùng GCM với IV ngẫu nhiên + AuthTag xác thực toàn vẹn |
| Mật khẩu yếu | Enforce chính sách + hiển thị độ mạnh realtime |
| Injection | Parameterized query toàn bộ (mysql-connector) |

---

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Giao diện web | Streamlit |
| Hash mật khẩu | Argon2id (argon2-cffi) |
| Mã hóa dữ liệu | AES-256-GCM (cryptography) |
| CSDL | MySQL |
| Kết nối DB | mysql-connector-python |
| Containerization | Docker + Docker Compose |
| Biến môi trường | python-dotenv |

---

## Cài đặt & Chạy

### Cách 1 — Docker (khuyến nghị)

```bash
cp .env.example .env
# Chỉnh DB_PASSWORD và MASTER_KEY trong .env
docker-compose up --build
```

Truy cập: `http://localhost:8501`

### Cách 2 — Chạy thủ công

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Chỉnh thông tin DB và MASTER_KEY

streamlit run app.py        # Giao diện web
python main.py              # Giao diện CLI
```

Tạo `MASTER_KEY` (32 byte hex):
```bash
python -c "import os; print(os.urandom(32).hex())"
```

### Chạy demo & kiểm tra

```bash
python demo_weaknesses.py       # Demo 4 điểm yếu bảo mật
python test_bulk_passwords.py   # Kiểm tra hàng loạt mật khẩu
```

---

## Cấu trúc dự án

```
PasswordSecurity/
├── app.py                    # Giao diện web Streamlit (PassGuard)
├── main.py                   # CLI menu chính
├── demo_weaknesses.py        # Demo 4 điểm yếu bảo mật
├── test_bulk_passwords.py    # Kiểm tra hàng loạt mật khẩu
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── modules/
│   ├── auth.py               # Đăng ký, đăng nhập, profile, đổi mật khẩu
│   ├── database.py           # MySQL CRUD, auto-init schema
│   ├── encryption.py         # AES-256-GCM encrypt/decrypt
│   ├── logger.py             # log_activity → file + DB
│   └── password_utils.py     # Argon2 hash/verify, kiểm tra độ mạnh
└── tests/
    ├── test_passwords.txt    # 25 mật khẩu mẫu
    └── sample_data.sql       # 6 user mẫu (PII đã mã hóa)
```

---

## Lưu ý bảo mật

- `MASTER_KEY` là khóa duy nhất giải mã PII — không commit lên git, không chia sẻ
- Thay đổi `MASTER_KEY` khiến dữ liệu cũ không giải mã được
- IP trong log là mô phỏng (local + random) cho mục đích demo
- Chạy trong môi trường Lab (Docker/VM) theo khuyến nghị của đề tài

---

*Dự án phát triển cho mục đích học tập — Môn An toàn thông tin*
