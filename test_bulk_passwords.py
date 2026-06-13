"""
test_bulk_passwords.py — Kiểm tra độ mạnh hàng loạt mật khẩu từ file.
Đọc từ: test/test_passwords.txt
Chạy:   python test_bulk_passwords.py
"""

import os
import sys

# Thêm thư mục gốc vào sys.path để import password_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.password_utils import check_password_strength

TEST_FILE = os.path.join(os.path.dirname(__file__), "test", "test_passwords.txt")

# Màu sắc terminal
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

# Màu tương ứng với từng mức độ
STRENGTH_COLOR = {
    "Yếu":       RED,
    "Trung bình": YELLOW,
    "Mạnh":      GREEN,
}

STRENGTH_ICON = {
    "Yếu":       "✘",
    "Trung bình": "⚠",
    "Mạnh":      "✔",
}


def load_passwords(filepath: str) -> list[str]:
    """Đọc file, bỏ qua dòng trống và dòng bắt đầu bằng #."""
    passwords = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                passwords.append(line)
    return passwords


def truncate(text: str, max_len: int = 25) -> str:
    """Rút gọn mật khẩu dài để hiển thị gọn trong bảng."""
    return text if len(text) <= max_len else text[:max_len - 3] + "..."


def print_table(results: list[tuple[int, str, str]]):
    """In bảng kết quả STT | Mật khẩu | Mức độ."""
    col_stt  = 5
    col_pass = 27
    col_str  = 14

    # Header
    print()
    print(f"  {BOLD}{'STT':<{col_stt}} {'Mật khẩu':<{col_pass}} {'Mức độ':<{col_str}}{RESET}")
    print(f"  {'─'*col_stt} {'─'*col_pass} {'─'*col_str}")

    for stt, password, strength in results:
        color = STRENGTH_COLOR[strength]
        icon  = STRENGTH_ICON[strength]
        display = truncate(password, col_pass - 1)
        print(
            f"  {DIM}{stt:<{col_stt}}{RESET} "
            f"{display:<{col_pass}} "
            f"{color}{icon} {strength:<{col_str - 2}}{RESET}"
        )

    print(f"  {'─'*col_stt} {'─'*col_pass} {'─'*col_str}")


def print_summary(results: list[tuple[int, str, str]]):
    """In thống kê số lượng và tỷ lệ % từng mức độ."""
    total = len(results)
    counts = {"Yếu": 0, "Trung bình": 0, "Mạnh": 0}
    for _, _, strength in results:
        counts[strength] += 1

    print(f"\n  {BOLD}THỐNG KÊ KẾT QUẢ ({total} mật khẩu){RESET}")
    print(f"  {'─'*40}")

    for strength, count in counts.items():
        color   = STRENGTH_COLOR[strength]
        icon    = STRENGTH_ICON[strength]
        percent = (count / total * 100) if total > 0 else 0
        bar     = "█" * int(percent / 5)  # mỗi █ = 5%
        print(
            f"  {color}{icon} {strength:<12}{RESET} "
            f"{count:>3} mật khẩu  ({percent:5.1f}%)  {color}{bar}{RESET}"
        )

    print(f"  {'─'*40}")
    print(f"  Tổng cộng:    {total:>3} mật khẩu")


def main():
    print(f"\n{BOLD}{'='*52}")
    print("  KIỂM TRA ĐỘ MẠNH MẬT KHẨU HÀNG LOẠT")
    print(f"{'='*52}{RESET}")
    print(f"  File: {TEST_FILE}")

    # Đọc file
    try:
        passwords = load_passwords(TEST_FILE)
    except FileNotFoundError:
        print(f"\n  {RED}Lỗi: Không tìm thấy file '{TEST_FILE}'{RESET}")
        print(f"  Hãy đảm bảo file tồn tại và đường dẫn đúng.")
        sys.exit(1)

    if not passwords:
        print(f"\n  {YELLOW}File không có mật khẩu nào để kiểm tra.{RESET}")
        sys.exit(0)

    print(f"  Đã đọc {len(passwords)} mật khẩu.\n")

    # Kiểm tra từng mật khẩu
    results = []
    for i, pw in enumerate(passwords, start=1):
        strength = check_password_strength(pw)
        results.append((i, pw, strength))

    # In bảng và thống kê
    print_table(results)
    print_summary(results)
    print()


if __name__ == "__main__":
    main()
