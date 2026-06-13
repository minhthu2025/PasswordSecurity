# PasswordSecurity

Hệ thống quản lý mật khẩu và xác thực người dùng dạng **Console (CLI)** được viết bằng Python. Dự án tập trung vào bảo mật thực tế: hash mật khẩu mạnh, mã hóa dữ liệu cá nhân, chống brute-force và ghi log hoạt động.

## Mô tả

Ứng dụng cho phép người dùng:
- Đăng ký tài khoản với thông tin cá nhân (họ tên, email, SĐT, CMND/CCCD, địa chỉ)
- Đăng nhập an toàn (hỗ trợ username hoặc email)
- Xem và cập nhật thông tin cá nhân
- Đổi mật khẩu
- Kiểm tra độ mạnh bất kỳ mật khẩu nào (không cần đăng nhập)
- Kiểm tra hàng loạt mật khẩu từ file và xem thống kê

Tất cả dữ liệu nhạy cảm được **mã hóa tại rest**, mật khẩu được **hash bằng Argon2id**, và có cơ chế **khóa tài khoản tạm thời** khi đăng nhập sai nhiều lần.

## Tính năng nổi bật

- **Mã hóa dữ liệu cá nhân (PII)**: Họ tên, email, SĐT, CMND/CCCD, địa chỉ được mã hóa bằng **AES-256-GCM** (key 32 byte từ `MASTER_KEY` trong `.env` dạng hex).
- **Hash mật khẩu an toàn**: Sử dụng **Argon2id** (memory-hard) với cấu hình mạnh (`time_cost=2`, `memory=100MiB`, `parallelism=8`).
- **Chính sách mật khẩu**:
  - Tối thiểu 6 ký tự
  - Phải chứa chữ hoa, chữ thường, số và ký tự đặc biệt
  - Hiển thị độ mạnh: Yếu / Trung bình / Mạnh
- **Bảo vệ brute-force**: Khóa tài khoản **3 phút** sau **5 lần đăng nhập sai**.
- **Validation chặt chẽ**: Username (6–20 ký tự, không chứa từ cấm), email, SĐT (10 số), CMND/CCCD (12 số).
- **Kiểm tra độ mạnh hàng loạt**: `test_bulk_passwords.py` đọc `tests/test_passwords.txt`, in bảng kết quả có màu và thống kê tỷ lệ từng mức.
- **Logging hoạt động**: Mọi hành động ghi log ra console (kèm IP) và lưu vào bảng `activity_logs`.
- **Tự động khởi tạo CSDL**: Tạo database, bảng `users` và `activity_logs`, tự động thêm cột khi schema thay đổi.

## Công nghệ sử dụng

| Thành phần              | Công nghệ                     |
|-------------------------|-------------------------------|
| Ngôn ngữ                | Python 3.10+                  |
| Hash mật khẩu           | Argon2id (argon2-cffi)        |
| Mã hóa dữ liệu          | AES-GCM 256 (cryptography)    |
| CSDL                    | MySQL                         |
| Kết nối DB              | mysql-connector-python        |
| Quản lý biến môi trường | python-dotenv                 |

## Yêu cầu

- Python 3.10 trở lên
- MySQL Server (local hoặc remote)
- (Khuyến nghị) Virtual environment

## Hướng dẫn cài đặt & chạy

### 1. Chuẩn bị môi trường

```bash
python3 -m venv venv
source venv/bin/activate       # Linux/macOS
# venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

### 2. Cấu hình file `.env`

Tạo file `.env` ở thư mục gốc (cùng cấp `main.py`):

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_strong_password
DB_NAME=password_security

MASTER_KEY=your64characterhexkeyhere1234567890abcdef1234567890abcdef12
```

Tạo `MASTER_KEY` mới:

```bash
python -c "import os; print(os.urandom(32).hex())"
```

### 3. Chạy ứng dụng chính

```bash
python main.py
```

Ứng dụng tự động kết nối MySQL, tạo database và bảng nếu chưa có.

### 4. Nạp dữ liệu mẫu (tùy chọn)

```bash
mysql -u root -p password_security < tests/sample_data.sql
```

> **Lưu ý**: `sample_data.sql` được sinh ra với một `MASTER_KEY` cụ thể. Nếu dùng `MASTER_KEY` khác, dữ liệu PII sẽ không giải mã được.

### 5. Kiểm tra hàng loạt mật khẩu

```bash
python test_bulk_passwords.py
```

Đọc 25 mật khẩu mẫu từ `tests/test_passwords.txt`, in bảng kết quả và thống kê.

### 6. Demo điểm yếu bảo mật

```bash
python demo_weaknesses.py
```

Không cần DB hay `.env`. Chạy độc lập hoàn toàn.

## Cấu trúc dự án

```
PasswordSecurity/
├── main.py                   # CLI menu chính, xử lý tương tác người dùng
├── demo_weaknesses.py        # Demo 4 điểm yếu bảo mật (báo cáo + thuyết trình)
├── test_bulk_passwords.py    # Kiểm tra hàng loạt mật khẩu từ file, in bảng + thống kê
├── requirements.txt
├── .env                      # (không commit) DB credentials + MASTER_KEY
├── .gitignore
├── README.md
├── modules/
│   ├── auth.py               # Logic đăng ký, đăng nhập, cập nhật profile, đổi mật khẩu
│   ├── database.py           # Kết nối MySQL, CRUD, tự động init schema + migration
│   ├── encryption.py         # encrypt_value / decrypt_value dùng AES-256-GCM + MASTER_KEY
│   ├── logger.py             # get_client_ip() + log_activity (in log + lưu DB)
│   └── password_utils.py     # Argon2 hash/verify, độ mạnh mật khẩu, validation
└── tests/
    ├── test_passwords.txt    # 25 mật khẩu mẫu (4 nhóm: quá ngắn, thiếu ký tự, trung bình, mạnh)
    └── sample_data.sql       # Dữ liệu mẫu 6 user (PII đã mã hóa, password đã hash)
```

## Luồng sử dụng điển hình

1. **Đăng ký** → Nhập thông tin → Kiểm tra độ mạnh + validation → Hash Argon2 + Encrypt AES-GCM → Lưu DB + Log
2. **Đăng nhập** → Kiểm tra khóa tài khoản → Xác thực Argon2 → Hiển thị thông tin + kiểm tra bảo mật mật khẩu
3. **Xem/Cập nhật Profile** → Decrypt khi hiển thị, encrypt khi lưu lại
4. **Đổi mật khẩu** → Xác thực mật khẩu cũ → Hash mật khẩu mới
5. **Mọi hành động** đều ghi log ra console:

```
[2026-06-12 17:21:15] [LOGIN_SUCCESS] user_id=42   ip=10.140.58.242   | Đăng nhập thành công
```

## Demo điểm yếu bảo mật (`demo_weaknesses.py`)

| Demo | Nội dung |
|------|----------|
| 1    | Rainbow Table Attack — MD5 không salt bị crack ngay; Argon2 với salt miễn nhiễm |
| 2    | AES-ECB lộ pattern vs AES-GCM — khối plaintext giống nhau → ciphertext giống nhau |
| 3    | Benchmark Argon2 — đo thời gian hash thực tế theo `memory_cost` (8MB / 32MB / 64MB) |
| 4    | Argon2 memory-hard vs GPU brute-force — ước tính thời gian crack theo VRAM |

## Dữ liệu mẫu (`tests/sample_data.sql`)

6 user mẫu phục vụ các tình huống demo khác nhau:

| Username   | Password           | Kịch bản demo                           |
|------------|--------------------|-----------------------------------------|
| nguyenvana | MyP@ssw0rd2026!    | Tài khoản đầy đủ thông tin             |
| tranthib   | Secure#Hash99XY    | Thiếu CMND và địa chỉ                  |
| levanc     | Dragon$Fly2026#    | Tài khoản đang bị khóa (5 lần sai)     |
| phamthid   | CorrectH0rse!99    | Đã sai 3/5 lần — chưa bị khóa          |
| hoangvane  | Admin@Secure123!   | Demo đổi mật khẩu                       |
| vuthif     | Bl@ckP4nther_99!   | Tài khoản sinh viên, thông tin tối thiểu |

## Bảo mật & Lưu ý quan trọng

- **MASTER_KEY** là chìa khóa duy nhất để giải mã PII. Không commit, không chia sẻ.
- Thay đổi `MASTER_KEY` → dữ liệu cũ trong DB sẽ **không giải mã được** (cần re-encrypt thủ công).
- Mật khẩu **không bao giờ lưu plaintext**.
- IP trong log là **mô phỏng** (local + random) cho mục đích demo Console. Môi trường thực cần lấy IP từ request.

## Giấy phép

Dự án phát triển cho mục đích học tập và minh họa kỹ thuật bảo mật cơ bản.
