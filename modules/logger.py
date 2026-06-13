import socket
import random
from datetime import datetime

from modules.database import log_activity as _db_log_activity


# ============================================================
# HÀM LẤY IP KẾT HỢP LOCAL + RANDOM (dành cho Console demo logging)
# ============================================================

def _get_local_ip() -> str:
    """Lấy địa chỉ IP local (LAN) thực tế của máy đang chạy Console.

    Cách làm: tạo socket UDP kết nối tạm đến DNS công cộng (8.8.8.8)
    rồi đọc sockname để biết IP của interface đang dùng.
    Không cần quyền đặc biệt, không gọi API bên ngoài.
    Fallback về 127.0.0.1 nếu không xác định được (ví dụ: không có mạng).
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.3)
        # Kết nối "giả" để hệ thống chọn interface phù hợp
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def get_client_ip() -> str:
    """Trả về IP "client" để ghi vào log.

    Thiết kế: "IP Random (kết hợp với Local)" dùng để minh họa logging trong app Console.
    - Ưu tiên IP Local thực (127.0.0.1 hoặc 192.168.x.x / 10.x...) khi chạy trên máy developer.
    - Xen kẽ ngẫu nhiên các IP "remote" giả lập (từ dải TEST-NET RFC5737 và private range)
      để activity log trông đa dạng, giống như có nhiều người dùng từ nhiều nơi truy cập.

    Mỗi lần gọi log_activity có thể nhận IP khác nhau → dễ thấy sự "kết hợp" khi xem log.
    Giá trị trả về luôn là chuỗi IP sạch (dùng để lưu DB và hiển thị).
    """
    local_ip = _get_local_ip()

    # Danh sách IP mô phỏng "khách hàng từ xa" (dùng cho mục đích demo, không phải IP thật)
    simulated_pool = [
        "203.0.113.45",   # TEST-NET-1 (RFC 5737) - dành riêng cho ví dụ tài liệu
        "203.0.113.177",
        "198.51.100.23",  # TEST-NET-2
        "192.0.2.99",     # TEST-NET-3
        f"10.{random.randint(1, 254)}.{random.randint(0, 254)}.{random.randint(1, 254)}",
        f"172.16.{random.randint(0, 254)}.{random.randint(1, 254)}",
        f"192.168.10.{random.randint(10, 250)}",
    ]

    # Xác suất kết hợp:
    # ~65% trả local_ip (thực tế khi dùng Console trên cùng máy/LAN)
    # ~35% trả IP random mô phỏng từ xa (để log đẹp, đa dạng, dễ minh họa)
    if random.random() < 0.65:
        return local_ip
    else:
        return random.choice(simulated_pool)


# ============================================================
# HÀM LOG_ACTIVITY - GHI LOG ĐẸP, RÕ RÀNG + TỰ ĐỘNG LẤY IP
# ============================================================

def log_activity(user_id: int | None, action: str, details: str | None = None):
    """Ghi nhận hoạt động của người dùng / hệ thống.

    Tách biệt rõ ràng:
    - Dòng log chi tiết dạng [YYYY-MM-DD HH:MM:SS] [...] được ghi vào file app.log (không in ra console).
    - Thông tin người dùng nhìn thấy (console output) được xử lý riêng ở main.py và các hàm auth trả về message đơn giản.
    - Vẫn ghi đầy đủ vào bảng activity_logs trong MySQL.

    Quy trình:
    1. Tự động gọi get_client_ip() để lấy IP (kết hợp local + random).
    2. Ghi dòng log chi tiết vào app.log.
    3. Lưu vào database (giữ nguyên).
    """
    ip = get_client_ip()
    local_ip = _get_local_ip()

    # Tạo chuỗi IP hiển thị đẹp (kết hợp local nếu khác)
    if ip == local_ip:
        ip_display = ip
    else:
        ip_display = f"{ip} (local={local_ip})"

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detail_str = details or ""

    # === GHI LOG CHI TIẾT VÀO FILE (app.log) - tách biệt khỏi console output ===
    log_line = f"[{ts}] [{action}] user_id={user_id or 'N/A':<4} ip={ip_display:<30} | {detail_str}"
    try:
        with open("app.log", "a", encoding="utf-8") as log_file:
            log_file.write(log_line + "\n")
    except Exception:
        # Không để lỗi ghi log file ảnh hưởng đến luồng chương trình
        pass

    # === LƯU VÀO DATABASE (giữ nguyên logic) ===
    try:
        # Gọi DB layer với IP (DB đã được cập nhật để nhận ip_address)
        _db_log_activity(user_id, action, details, ip_address=ip)
    except TypeError:
        # Fallback tương thích ngược nếu DB layer chưa có tham số ip_address (tránh crash)
        _db_log_activity(user_id, action, details)


# ============================================================
# CÁC HẰNG ACTION (giữ nguyên để tương thích với auth.py, main.py)
# ============================================================

# Predefined action constants for consistency across the app
ACTION_REGISTER = "REGISTER"
ACTION_LOGIN_SUCCESS = "LOGIN_SUCCESS"
ACTION_LOGIN_FAILED = "LOGIN_FAILED"
ACTION_LOGIN_LOCKED = "LOGIN_LOCKED"
ACTION_LOGOUT = "LOGOUT"
ACTION_UPDATE_PROFILE = "UPDATE_PROFILE"
ACTION_CHANGE_PASSWORD = "CHANGE_PASSWORD"
