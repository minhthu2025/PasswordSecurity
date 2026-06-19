# BTL — Tài liệu cấu trúc dự án PassGuard

Dự án **PassGuard** (PasswordSecurity) — Đề tài 12: Công cụ kiểm tra độ mạnh mật khẩu & mã hóa dữ liệu cá nhân.

---

## 1. Cấu trúc dự án & vai trò từng file

```
PasswordSecurity/
├── app.py                    # Giao diện web Streamlit (PassGuard)
├── main.py                   # Giao diện CLI (menu dòng lệnh)
├── test_bulk_passwords.py    # Script kiểm tra độ mạnh hàng loạt
├── demo_weaknesses.py        # Demo 4 điểm yếu bảo mật (tham khảo lý thuyết)
├── requirements.txt          # Thư viện Python
├── Dockerfile                # Image Docker cho app Streamlit
├── docker-compose.yml        # Orchestration: MySQL + app
├── .env.example              # Mẫu biến môi trường
├── command.md                # Lệnh chạy chuẩn
├── .streamlit/config.toml    # Cấu hình theme Streamlit
├── modules/
│   ├── password_utils.py     # Băm Argon2id + kiểm tra độ mạnh mật khẩu
│   ├── encryption.py         # Mã hóa/giải mã AES-256-GCM
│   ├── database.py           # Kết nối MySQL, CRUD, schema
│   ├── auth.py               # Logic nghiệp vụ: đăng ký, đăng nhập, profile
│   └── logger.py             # Ghi log file + database
└── tests/
    ├── test_passwords.txt    # 25 mật khẩu mẫu để test
    └── sample_data.sql       # Dữ liệu user mẫu (PII đã mã hóa)
```

### Bảng vai trò tổng quan

| File | Vai trò trong hệ thống | Phụ thuộc chính |
|------|------------------------|----------------|
| `password_utils.py` | Lớp bảo mật mật khẩu: hash Argon2id, verify, đánh giá độ mạnh, validate input | `argon2-cffi` |
| `encryption.py` | Lớp mã hóa dữ liệu nhạy cảm (PII) tại rest bằng AES-256-GCM | `cryptography`, `.env` |
| `database.py` | Lớp truy cập dữ liệu: kết nối MySQL, tạo bảng, CRUD user/log | `mysql-connector`, `encryption` |
| `auth.py` | Lớp nghiệp vụ: orchestrate validate → hash → encrypt → lưu DB → log | `password_utils`, `encryption`, `database`, `logger` |
| `logger.py` | Lớp ghi nhật ký: file `app.log` + bảng `activity_logs` | `database` |
| `main.py` | Presentation CLI: menu, nhập liệu, gọi `auth` | `auth`, `password_utils`, `database` |
| `app.py` | Presentation Web: UI Streamlit, session, routing trang | `auth`, `password_utils`, `database` |
| `test_bulk_passwords.py` | Công cụ kiểm thử hàng loạt mật khẩu | `password_utils` |
| `demo_weaknesses.py` | Minh họa lý thuyết: Rainbow Table, ECB vs GCM, benchmark Argon2 | độc lập |

### Luồng dữ liệu chính

```
Người dùng (CLI / Web)
        ↓
   main.py / app.py          ← Presentation
        ↓
     auth.py                  ← Business logic
   ↙    ↓    ↘
password_utils  encryption  database
   (hash)        (PII)      (MySQL)
        ↘         ↓         ↙
              logger.py
```

---

## 2. Chi tiết từng file & danh sách hàm

---

### 2.1 `modules/password_utils.py`

**Vai trò:** Module lõi về mật khẩu — băm an toàn (Argon2id), xác thực hash, đánh giá độ mạnh, validate username/email/phone/CMND.

**Hằng số quan trọng:**

| Hằng số | Giá trị | Ý nghĩa |
|---------|---------|---------|
| `ph` (PasswordHasher) | `time_cost=2`, `memory_cost=102400` (100 MiB), `parallelism=8`, `hash_len=32`, `salt_len=16` | Cấu hình Argon2id toàn dự án |
| `FORBIDDEN_USERNAMES` | 17 từ cấm (`admin`, `root`, ...) | Chống username dễ đoán |

| Hàm | Công dụng |
|-----|-----------|
| `hash_password(password)` | Băm mật khẩu bằng Argon2id, trả chuỗi hash (có salt nhúng sẵn) |
| `verify_password(password, password_hash)` | So khớp mật khẩu với hash đã lưu; trả `True`/`False` |
| `meets_password_requirements(password)` | Kiểm tra đủ 4 loại ký tự + độ dài ≥ 8 |
| `get_password_strength(password)` | Phân loại `Weak` / `Medium` / `Strong` (tiếng Anh) |
| `check_password_strength(password)` | Phân loại `Yếu` / `Trung bình` / `Mạnh` (tiếng Việt) |
| `get_password_requirements_message()` | Trả thông báo lỗi chuẩn khi mật khẩu không đủ điều kiện |
| `is_valid_username(username)` | Validate username; trả `(bool, message)` |
| `is_valid_email(email)` | Validate định dạng email bằng regex |
| `is_valid_phone(phone)` | Validate 10 chữ số (tùy chọn — `None` hợp lệ) |
| `is_valid_identify_card(identify_card)` | Validate CMND/CCCD 12 chữ số (tùy chọn) |
| `password_input(label, key, placeholder)` | Wrapper `st.text_input(type="password")` cho Streamlit |

#### ★ Phân tích kỹ: `PasswordHasher` (đối tượng `ph`)

```python
ph = PasswordHasher(
    time_cost=2,        # t — số vòng lặp nội bộ Argon2
    memory_cost=102400, # m — RAM tối thiểu 102400 KiB = 100 MiB
    parallelism=8,      # p — số luồng song song
    hash_len=32,        # độ dài output hash (byte)
    salt_len=16,        # salt ngẫu nhiên 16 byte/lần hash
)
```

- **Mục đích `memory_cost=100 MiB`:** Làm chậm brute-force trên GPU vì VRAM hạn chế — mỗi lần hash tốn ~100MB RAM.
- **Salt 16 byte:** Cùng mật khẩu → hash khác nhau → vô hiệu Rainbow Table.
- **Output mẫu:** `$argon2id$v=19$m=102400,t=2,p=8$<salt>$<hash>`

#### ★ Phân tích kỹ: `get_password_strength` / chính sách mật khẩu

| Mức | Điều kiện |
|-----|-----------|
| Weak (Yếu) | `< 8` ký tự **hoặc** thiếu 1 trong 4 loại (hoa/thường/số/đặc biệt) |
| Medium (Trung bình) | Đủ 4 loại, độ dài 8–11 |
| Strong (Mạnh) | Đủ 4 loại, độ dài ≥ 12 |

---

### 2.2 `modules/encryption.py`

**Vai trò:** Mã hóa/giải mã dữ liệu nhạy cảm (họ tên, email, SĐT, CMND, địa chỉ) trước khi lưu MySQL.

| Hàm | Công dụng |
|-----|-----------|
| `_load_master_key()` | Đọc khóa 32 byte từ `MASTER_KEY` (hex) hoặc `ENCRYPTION_KEY` (base64 legacy) |
| `encrypt_data(plaintext)` | Mã hóa AES-256-GCM → base64 (nonce + ciphertext + tag) |
| `decrypt_data(ciphertext)` | Giải mã + xác thực tag; lỗi → trả `None` (không crash) |
| `encrypt_value` / `decrypt_value` | Alias tương thích ngược — các module khác import tên này |

#### ★ Phân tích kỹ: `encrypt_data`

**Quy trình:**
1. Đọc `MASTER_KEY` (64 ký tự hex = 32 byte) từ `.env`
2. Sinh `nonce = os.urandom(12)` — 12 byte ngẫu nhiên mỗi lần mã hóa
3. `AESGCM(key).encrypt(nonce, plaintext_utf8, associated_data=None)`
4. Ghép `nonce + ciphertext` → encode base64 → lưu vào cột `TEXT` MySQL

**Tại sao 12 byte nonce?** Chuẩn NIST khuyến nghị 96-bit (12 byte) cho GCM.

**Tại sao base64?** Dễ lưu trong `TEXT`/`VARCHAR`, tránh lỗi encoding nhị phân.

#### ★ Phân tích kỹ: `decrypt_data`

1. Base64 decode → tách 12 byte đầu làm nonce, phần còn lại là ciphertext+tag
2. `AESGCM.decrypt()` tự kiểm tra AuthTag — nếu sai key hoặc dữ liệu bị sửa → `InvalidTag` → trả `None`
3. Thiết kế **fail-silent** (không raise) để app không crash khi dữ liệu cũ hỏng

---

### 2.3 `modules/database.py`

**Vai trò:** Lớp truy cập MySQL — kết nối, khởi tạo schema, CRUD user, quản lý lockout, ghi log DB.

**Hằng số:** `DB_CONFIG` — đọc `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` từ `.env`.

| Hàm | Công dụng |
|-----|-----------|
| `get_connection()` | Tạo kết nối MySQL; tự tạo database nếu chưa tồn tại |
| `get_cursor(commit=False)` | Context manager: mở cursor dictionary, tự đóng + commit |
| `init_db()` | Tạo bảng `users`, `activity_logs`; migrate cột thiếu |
| `_decrypt_user_row(row)` | Giải mã 5 cột PII khi đọc user từ DB |
| `create_user(user_data)` | INSERT user mới; trả `user_id` |
| `get_user_by_id(user_id)` | SELECT theo ID, tự decrypt PII |
| `get_user_by_username(username)` | SELECT theo username (không mã hóa) |
| `get_all_users()` | SELECT toàn bộ — dùng tra email trùng |
| `update_user_fields(user_id, fields)` | UPDATE động các cột được phép |
| `increment_failed_attempts(user_id)` | Tăng `failed_login_attempts`, trả số lần mới |
| `reset_failed_attempts(user_id)` | Reset counter + xóa `locked_until` |
| `set_user_locked(user_id, locked_until)` | Ghi thời điểm mở khóa |
| `log_activity(user_id, action, details, ip_address)` | INSERT vào `activity_logs` |

#### ★ Phân tích kỹ: Schema `users`

| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| `username` | `VARCHAR(20) UNIQUE` | Lưu plaintext — dùng đăng nhập |
| `password_hash` | `TEXT` | Argon2id hash — không decrypt |
| `full_name`, `email`, `phone`, `identify_card`, `address` | `TEXT` | Đã mã hóa AES-GCM (base64) |
| `failed_login_attempts` | `INT DEFAULT 0` | Đếm sai mật khẩu |
| `locked_until` | `DATETIME NULL` | Thời điểm hết khóa |

#### ★ Phân tích kỹ: `init_db` + migration

- Tạo bảng nếu chưa có (`CREATE TABLE IF NOT EXISTS`)
- Vòng lặp `ALTER TABLE ADD COLUMN` — bỏ qua lỗi nếu cột đã tồn tại → nâng cấp schema an toàn
- Charset `utf8mb4` — hỗ trợ tiếng Việt đầy đủ

#### ★ Phân tích kỹ: `_decrypt_user_row`

Chỉ decrypt 5 trường PII; **không** đụng `username` (cần tra cứu) và `password_hash` (đã là hash một chiều).

---

### 2.4 `modules/auth.py`

**Vai trò:** Orchestrator nghiệp vụ — kết hợp validate, hash, encrypt, DB, log thành các use-case hoàn chỉnh.

**Hằng số:**

| Hằng số | Giá trị | Ý nghĩa |
|---------|---------|---------|
| `MAX_FAILED_ATTEMPTS` | `5` | Số lần sai tối đa trước khi khóa |
| `LOCK_DURATION_MINUTES` | `3` | Thời gian khóa tài khoản |

| Hàm | Công dụng |
|-----|-----------|
| `_get_remaining_lock_time(locked_until)` | Format thời gian còn lại: `"2 phút 15 giây"` |
| `register_user(...)` | Validate → hash password → encrypt PII → `create_user` → log |
| `login_user(identifier, password)` | Tìm user → kiểm tra lock → verify → lockout/log |
| `get_user_profile(user_id)` | Proxy tới `get_user_by_id` |
| `update_user_profile(...)` | Validate thay đổi → encrypt → `update_user_fields` → log |
| `change_user_password(...)` | Verify cũ → validate mới → hash → update → reset lock |

#### ★ Phân tích kỹ: `login_user` — luồng lockout

```
1. Tìm user theo username (nhanh) hoặc email (quét get_all_users)
2. Nếu locked_until > now → từ chối + log LOGIN_LOCKED
3. Nếu locked_until đã hết → reset_failed_attempts
4. verify_password thất bại:
   - increment_failed_attempts
   - nếu attempts >= 5 → set_user_locked(now + 3 phút)
   - log LOGIN_FAILED
5. Thành công → reset_failed_attempts + log LOGIN_SUCCESS
```

**Thiết kế bảo mật:** Kiểm tra lock **trước** verify password — kể cả đúng mật khẩu vẫn không vào được khi đang khóa.

#### ★ Phân tích kỹ: `register_user` — pipeline dữ liệu

```
Input thô
  → is_valid_username / is_valid_email / is_valid_phone / is_valid_identify_card
  → meets_password_requirements
  → hash_password(password)           # 1 chiều, không decrypt
  → encrypt_value(full_name, email…)  # 2 chiều, cần MASTER_KEY
  → create_user(user_data)
  → log_activity(REGISTER)
```

---

### 2.5 `modules/logger.py`

**Vai trò:** Ghi nhật ký kép — file `app.log` (chi tiết) + bảng `activity_logs` (truy vấn).

| Hàm | Công dụng |
|-----|-----------|
| `_get_local_ip()` | Lấy IP LAN thực qua socket UDP tới `8.8.8.8` |
| `get_client_ip()` | 65% IP local / 35% IP mô phỏng (demo) |
| `log_activity(user_id, action, details)` | Ghi file + gọi `database.log_activity` kèm IP |

**Hằng số ACTION:** `REGISTER`, `LOGIN_SUCCESS`, `LOGIN_FAILED`, `LOGIN_LOCKED`, `LOGOUT`, `UPDATE_PROFILE`, `CHANGE_PASSWORD`

#### ★ Phân tích kỹ: `log_activity`

Format file log:
```
[2026-06-18 10:30:00] [LOGIN_SUCCESS] user_id=3    ip=192.168.1.5              | Đăng nhập thành công...
```

- Ghi file **không** in ra console — tách biệt UX và audit trail
- `try/except` khi ghi file — lỗi log không làm crash app
- Fallback `TypeError` nếu DB layer cũ chưa có `ip_address`

---

### 2.6 `main.py` — Giao diện CLI

**Vai trò:** Menu tương tác terminal — không chứa logic bảo mật, chỉ gọi `auth` và `password_utils`.

| Hàm | Công dụng |
|-----|-----------|
| `clear_screen()` | Xóa màn hình (`clear`/`cls`) |
| `print_header(title)` | In tiêu đề có viền `===` |
| `input_nonempty(prompt)` | Nhập đến khi không rỗng |
| `do_check_password()` | Kiểm tra độ mạnh mật khẩu bất kỳ (không cần đăng nhập) |
| `main_menu()` | Menu chính: Đăng ký / Đăng nhập / Kiểm tra / Thoát |
| `do_register()` | Form đăng ký → `register_user()` |
| `do_login()` | Form đăng nhập → `login_user()` → `user_session()` |
| `user_session(user)` | Menu sau đăng nhập: đổi MK / xem / sửa profile |
| `view_profile(user_id)` | Hiển thị PII đã decrypt |
| `update_profile(user_id)` | Form cập nhật → `update_user_profile()` |
| `change_password(user_id)` | Form đổi MK → `change_user_password()` |

**Entry point:** `init_db()` → `main_menu()`

---

### 2.7 `app.py` — Giao diện Web Streamlit

**Vai trò:** UI web PassGuard — session state, routing trang, CSS tùy chỉnh, gọi `auth`.

| Hàm | Công dụng |
|-----|-----------|
| `_inject_custom_css()` | Inject theme xanh #2563EB, sidebar tối, form card |
| `_render_hero()` | Banner giới thiệu (chưa đăng nhập) |
| `_page_header(title, subtitle)` | Header gradient mỗi trang |
| `_profile_field(label, value)` | Card hiển thị 1 trường profile |
| `_show_strength_badge(password)` | Badge độ mạnh realtime (error/warning/success) |
| `_init_session_state()` | Khởi tạo `user`, `page`, `db_ready` |
| `_setup_database()` | `@st.cache_resource` — gọi `init_db()` một lần |
| `_is_logged_in()` | Kiểm tra `st.session_state.user` |
| `_logout()` | Xóa session + log LOGOUT |
| `_nav_to(page_key)` | Chuyển trang + `st.rerun()` |
| `page_register()` | Form đăng ký web |
| `page_login()` | Form đăng nhập + hiển thị metric |
| `page_check_password()` | Kiểm tra độ mạnh (plaintext hiển thị — demo) |
| `page_view_profile()` | Xem profile 2 cột |
| `page_update_profile()` | Form cập nhật profile |
| `page_change_password()` | Form đổi mật khẩu |
| `_sidebar_nav_button(...)` | Nút điều hướng sidebar |
| `_render_sidebar()` | Sidebar: logo, user, menu |
| `_render_page()` | Router: map `page_key` → hàm trang |
| `main()` | Entry: CSS → DB → sidebar → hero → page |

#### ★ Phân tích kỹ: Session & routing

```python
PUBLIC_PAGES = {"Đăng ký": "register", "Đăng nhập": "login", ...}
AUTH_PAGES   = {"Xem Profile": "view_profile", "Đăng xuất": "logout", ...}
```

- Trang `auth_only` redirect về login nếu chưa đăng nhập
- `_setup_database` dùng `@st.cache_resource` — tránh gọi `init_db()` mỗi lần rerun

---

### 2.8 `test_bulk_passwords.py`

**Vai trò:** Script kiểm thử — đọc `tests/test_passwords.txt`, phân loại, in bảng + thống kê %.

| Hàm | Công dụng |
|-----|-----------|
| `load_passwords(filepath)` | Đọc file, bỏ dòng `#` và dòng trống |
| `truncate(text, max_len)` | Rút gọn mật khẩu dài khi in bảng |
| `print_table(results)` | In bảng STT \| Mật khẩu \| Mức độ (có màu ANSI) |
| `print_summary(results)` | Thống kê số lượng + % + bar chart ASCII |
| `main()` | Entry point |

---

### 2.9 File cấu hình & triển khai

| File | Vai trò |
|------|---------|
| `Dockerfile` | Image Python 3.12-slim, CMD `streamlit run app.py` port 8501 |
| `docker-compose.yml` | Service `db` (MySQL 8.0, port 3307) + `app` (Streamlit, port 8501) |
| `.env.example` | Mẫu `DB_*`, `MASTER_KEY` |
| `requirements.txt` | `argon2-cffi`, `cryptography`, `mysql-connector-python`, `python-dotenv`, `streamlit` |
| `.streamlit/config.toml` | Port 8501, theme xanh, tắt usage stats |
| `command.md` | Hướng dẫn lệnh Docker & chạy thủ công |

---

## 3. Phân công học tập cho 2 người

Nguyên tắc phân chia: **tách theo lớp kiến thức**, không tách theo chức năng người dùng (đăng ký/đăng nhập) để tránh 2 người cùng sửa `auth.py` và hiểu lẫn.

```
┌─────────────────────────────────────────────────────────────┐
│  NGƯỜI 1 — Lớp Mật khẩu & Mã hóa (Cryptography Layer)      │
│  "Tôi làm cho dữ liệu AN TOÀN trước khi lưu"                │
├─────────────────────────────────────────────────────────────┤
│  NGƯỜI 2 — Lớp Ứng dụng & Dữ liệu (Application Layer)       │
│  "Tôi làm cho hệ thống CHẠY ĐÚNG và người dùng TƯƠNG TÁC"   │
└─────────────────────────────────────────────────────────────┘
         ↕ Giao diện kết nối: auth.py gọi hàm export từ Người 1
```

---

### 👤 Người 1 — Chuyên trách Mật khẩu & Mã hóa

**File phụ trách (sở hữu 100%):**

| File | Lý do |
|------|-------|
| `modules/password_utils.py` | Toàn bộ Argon2id, chính sách mật khẩu, validate input |
| `modules/encryption.py` | Toàn bộ AES-256-GCM, MASTER_KEY |
| `test_bulk_passwords.py` | Kiểm thử module mật khẩu |
| `demo_weaknesses.py` | Demo lý thuyết (Rainbow Table, ECB vs GCM, benchmark) |

**Kiến thức phải nắm vững:**

1. **Argon2id:** ý nghĩa `time_cost`, `memory_cost`, `parallelism`, `salt_len`
2. **Chính sách mật khẩu:** 3 mức Yếu/Trung bình/Mạnh, 4 loại ký tự bắt buộc
3. **AES-256-GCM:** nonce 12 byte, AuthTag, tại sao không dùng ECB
4. **MASTER_KEY:** cách tạo, lưu `.env`, hậu quả đổi key
5. **Rainbow Table & brute-force:** lý do salt + memory-hard

**Hàm export cho Người 2 sử dụng (không được đổi tên/chữ ký):**

```python
# password_utils.py
hash_password, verify_password
meets_password_requirements, get_password_strength, check_password_strength
get_password_requirements_message
is_valid_username, is_valid_email, is_valid_phone, is_valid_identify_card
password_input  # chỉ Streamlit

# encryption.py
encrypt_value, decrypt_value  # alias của encrypt_data/decrypt_data
```

**Câu hỏi ôn tập Người 1:**
- Tại sao `memory_cost=100 MiB` chống được GPU brute-force?
- Cùng mật khẩu hash 2 lần, kết quả có giống nhau không? Vì sao?
- `decrypt_data` trả `None` thay vì raise exception — lợi ích gì?
- Nếu mất `MASTER_KEY`, dữ liệu PII trong DB còn đọc được không?

**KHÔNG phụ trách:** MySQL schema, lockout, Streamlit UI, Docker, `auth.py` logic.

---

### 👤 Người 2 — Chuyên trách Ứng dụng & Dữ liệu

**File phụ trách (sở hữu 100%):**

| File | Lý do |
|------|-------|
| `modules/database.py` | MySQL, schema, CRUD, decrypt khi đọc |
| `modules/auth.py` | Nghiệp vụ đăng ký/đăng nhập/lockout |
| `modules/logger.py` | Audit log file + DB |
| `main.py` | Giao diện CLI |
| `app.py` | Giao diện Streamlit |
| `Dockerfile`, `docker-compose.yml`, `.env.example`, `command.md` | Triển khai |

**Kiến thức phải nắm vững:**

1. **Schema MySQL:** bảng `users`, `activity_logs`, cột nào plaintext/hash/encrypted
2. **Luồng auth:** register → login → lockout 5 lần/3 phút → profile → đổi MK
3. **Parameterized query:** chống SQL injection (`%s` placeholder)
4. **Logger kép:** `app.log` vs `activity_logs`
5. **Streamlit:** session state, routing, `@st.cache_resource`
6. **Docker:** 2 service, biến môi trường, port 8501/3307

**Quy tắc khi gọi code Người 1:**

```python
# ĐÚNG — gọi hàm export, không tự implement hash/encrypt
password_hash = hash_password(password)
enc_email = encrypt_value(email)

# SAI — không viết MD5/SHA hoặc tự mã hóa trong auth.py/database.py
```

**Câu hỏi ôn tập Người 2:**
- Tại sao `username` lưu plaintext còn `email` lại mã hóa?
- Lockout kiểm tra trước hay sau `verify_password`? Tại sao?
- `_decrypt_user_row` gọi ở đâu, tại sao không decrypt `password_hash`?
- `docker compose up` khởi động gì, truy cập web ở URL nào?

**KHÔNG phụ trách:** Thuật toán Argon2, chi tiết AES-GCM, tham số `memory_cost`.

---

### 🤝 Ranh giới hợp tác (tránh lẫn lộn)

| Chủ đề | Người 1 | Người 2 |
|--------|---------|---------|
| Hash mật khẩu Argon2id | ✅ Sở hữu | ❌ Chỉ gọi `hash_password()` |
| Mã hóa PII AES-GCM | ✅ Sở hữu | ❌ Chỉ gọi `encrypt_value()` |
| Chính sách độ mạnh MK | ✅ Sở hữu | ❌ Chỉ hiển thị kết quả UI |
| Lockout 5 lần / 3 phút | ❌ | ✅ Sở hữu (`auth.py`) |
| Schema & CRUD MySQL | ❌ | ✅ Sở hữu (`database.py`) |
| Giao diện CLI / Web | ❌ | ✅ Sở hữu (`main.py`, `app.py`) |
| Activity logging | ❌ | ✅ Sở hữu (`logger.py`) |
| Docker / `.env` | ❌ | ✅ Sở hữu |
| Demo Rainbow Table / ECB | ✅ Sở hữu | ❌ Chỉ biết kết quả demo |

**File `auth.py` — chia trách nhiệm rõ:**

| Phần | Người phụ trách |
|------|-----------------|
| Gọi `hash_password`, `encrypt_value`, `is_valid_*` | Người 2 viết luồng; Người 1 cung cấp hàm |
| Logic lockout, tra user, ghi log | Người 2 |
| Thay đổi tham số Argon2 hoặc thuật toán mã hóa | Người 1 |

**Khi sửa code chung:**
1. Người 1 đổi `password_utils`/`encryption` → thông báo Người 2 nếu đổi tên hàm hoặc return type
2. Người 2 đổi schema DB → thông báo Người 1 nếu thêm cột cần mã hóa
3. Cả hai đọc `README.md` để nắm bức tranh tổng thể

---

## 4. Checklist trước báo cáo

### Người 1
- [ ] Giải thích được 5 tham số Argon2id trong `password_utils.py`
- [ ] Demo `hash_password` cùng input → 2 hash khác nhau
- [ ] Giải thích quy trình `encrypt_data` / `decrypt_data`
- [ ] Chạy `test_bulk_passwords.py` và giải thích kết quả
- [ ] Trình bày 1 demo từ `demo_weaknesses.py`

### Người 2
- [ ] Vẽ sơ đồ 2 bảng MySQL và loại dữ liệu mỗi cột
- [ ] Demo đăng ký → đăng nhập sai 5 lần → bị khóa
- [ ] Chỉ ra dòng log trong `app.log` và `activity_logs`
- [ ] Chạy `docker compose up` và trình diễn giao diện web
- [ ] Giải thích tại sao `auth.py` không tự hash/encrypt mà gọi module

---

*Tài liệu BTL — PassGuard / PasswordSecurity — Môn An toàn thông tin*