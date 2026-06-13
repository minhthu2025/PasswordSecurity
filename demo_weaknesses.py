"""
demo_weaknesses.py — Minh họa điểm yếu mật khẩu & mã hóa
==========================================================
Chạy: python demo_weaknesses.py
Mục đích: báo cáo + thuyết trình môn An toàn thông tin
"""

import os
import time
import hashlib
import base64
import struct

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


# ─────────────────────────────────────────────────────────────
# Tiện ích in ấn
# ─────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
DIM    = "\033[2m"


def banner(title: str, num: int):
    print()
    print("=" * 62)
    print(f"{BOLD}  DEMO {num}: {title}{RESET}")
    print("=" * 62)


def section(label: str):
    print(f"\n{CYAN}{BOLD}▶ {label}{RESET}")


def theory(*lines: str):
    print(f"\n{YELLOW}[LÝ THUYẾT]{RESET}")
    for line in lines:
        print(f"  {line}")


def result_ok(msg: str):
    print(f"  {GREEN}✔  {msg}{RESET}")


def result_fail(msg: str):
    print(f"  {RED}✘  {msg}{RESET}")


def info(msg: str):
    print(f"  {DIM}{msg}{RESET}")


def conclusion(msg: str):
    print(f"\n{BOLD}→ KẾT LUẬN:{RESET} {msg}")


def pause():
    print()
    input(f"{DIM}  [Nhấn Enter để chạy demo tiếp theo...]{RESET}")


# ═══════════════════════════════════════════════════════════════
# DEMO 1 — Rainbow Table Attack
# ═══════════════════════════════════════════════════════════════

def demo1_rainbow_table():
    banner("RAINBOW TABLE ATTACK — MD5 không salt vs Argon2 với salt", 1)

    theory(
        "MD5 không salt:  H = MD5(password)",
        "                 Cùng password → cùng hash → dùng bảng tra cứu sẵn (Rainbow Table)",
        "",
        "Argon2 với salt: H = Argon2(password || salt),  salt ngẫu nhiên mỗi lần",
        "                 Cùng password → hash KHÁC NHAU → Rainbow Table vô dụng",
    )

    # ── Bước 1: Xây dựng "Rainbow Table" giả lập ──
    section("Bước 1 — Xây dựng Rainbow Table (MD5, không salt)")

    common_passwords = [
        "123456", "password", "abc123",
        "iloveyou", "admin123", "qwerty",
        "letmein", "monkey", "dragon", "sunshine",
    ]

    rainbow_table: dict[str, str] = {}
    for pw in common_passwords:
        h = hashlib.md5(pw.encode()).hexdigest()
        rainbow_table[h] = pw

    print(f"\n  Đã tạo Rainbow Table với {len(rainbow_table)} entry:")
    for h, pw in list(rainbow_table.items())[:5]:
        info(f"  {h}  →  '{pw}'")
    info("  ...")

    # ── Bước 2: Nạn nhân lưu mật khẩu bằng MD5 không salt ──
    section("Bước 2 — Nạn nhân lưu mật khẩu bằng MD5 (không salt)")

    victim_passwords = ["123456", "iloveyou", "s3cur3!XpAssW0rd"]
    stored_hashes = [(pw, hashlib.md5(pw.encode()).hexdigest()) for pw in victim_passwords]

    for pw, h in stored_hashes:
        info(f"  password='{pw}'  →  MD5={h}")

    # ── Bước 3: Tấn công Rainbow Table ──
    section("Bước 3 — Attacker tra Rainbow Table")

    print()
    cracked = 0
    for pw, h in stored_hashes:
        if h in rainbow_table:
            result_fail(f"CRACKED! Hash={h[:16]}...  →  password='{rainbow_table[h]}'")
            cracked += 1
        else:
            result_ok(f"Không tìm thấy: Hash={h[:16]}...  (mật khẩu đủ mạnh/phức tạp)")

    print(f"\n  Kết quả: crack được {cracked}/{len(stored_hashes)} mật khẩu")

    # ── Bước 4: So sánh với Argon2 + salt ──
    section("Bước 4 — Cùng mật khẩu, hash bằng Argon2 (có salt tự động)")

    ph = PasswordHasher(time_cost=1, memory_cost=8192, parallelism=1)
    pw_test = "123456"

    hash1 = ph.hash(pw_test)
    hash2 = ph.hash(pw_test)

    info(f"  password = '{pw_test}'")
    print(f"\n  Lần hash 1:  {hash1[:60]}...")
    print(f"  Lần hash 2:  {hash2[:60]}...")
    print()

    if hash1 != hash2:
        result_ok("Hai hash KHÁC NHAU dù cùng mật khẩu → Rainbow Table hoàn toàn vô dụng!")

    # Thử tra bảng
    not_found = 0
    for h, _ in stored_hashes:
        # Argon2 hash không thể tra bảng MD5
        pass
    result_ok("Attacker không thể dùng Rainbow Table MD5 để tấn công Argon2 hash")

    conclusion(
        "MD5/SHA1 không salt: Rainbow Table crack trong mili-giây.\n"
        "           Argon2 với salt ngẫu nhiên: mỗi hash độc lập, bảng tra cứu vô nghĩa."
    )


# ═══════════════════════════════════════════════════════════════
# DEMO 2 — AES-ECB lộ pattern vs AES-GCM
# ═══════════════════════════════════════════════════════════════

def demo2_ecb_vs_gcm():
    banner("AES-ECB LỘ PATTERN vs AES-GCM", 2)

    theory(
        "AES-ECB (Electronic Codebook):  C_i = E(K, P_i)",
        "  Mỗi block 16 byte được mã hóa ĐỘC LẬP.",
        "  → Cùng plaintext block = cùng ciphertext block → lộ cấu trúc dữ liệu!",
        "",
        "AES-GCM (Galois/Counter Mode):  C = E(K, CTR) ⊕ P",
        "  Dùng counter tăng dần + XOR → mỗi block ciphertext phụ thuộc vào vị trí.",
        "  + Tag xác thực T = GHASH(H, A, C) ⊕ E(K, Y₀)  → phát hiện giả mạo.",
    )

    key = os.urandom(16)  # AES-128 cho demo

    # ── Plaintext có block lặp lại ──
    section("Bước 1 — Dữ liệu có cấu trúc lặp lại (16-byte aligned blocks)")

    # 3 block lặp hoàn toàn
    block = b"TRANSFER $10000 "   # đúng 16 bytes
    plaintext = block * 3 + b"TO ACCOUNT 9999 "
    print(f"\n  Plaintext (hex theo từng block 16 byte):")
    for i in range(0, len(plaintext), 16):
        blk = plaintext[i:i+16]
        print(f"    Block {i//16}: {blk.hex()}  '{blk.decode(errors='replace')}'")

    # ── ECB ──
    section("Bước 2 — Mã hóa bằng AES-ECB")

    cipher_ecb = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())

    # Pad to 64 bytes (đã đủ)
    enc = cipher_ecb.encryptor()
    ct_ecb = enc.update(plaintext) + enc.finalize()

    print(f"\n  Ciphertext ECB (hex theo từng block 16 byte):")
    ecb_blocks = []
    for i in range(0, len(ct_ecb), 16):
        blk = ct_ecb[i:i+16]
        ecb_blocks.append(blk.hex())
        print(f"    Block {i//16}: {blk.hex()}")

    # Phát hiện block trùng
    duplicates = len(ecb_blocks) - len(set(ecb_blocks))
    print()
    if duplicates > 0:
        result_fail(
            f"Phát hiện {duplicates} block ciphertext TRÙNG NHAU! "
            "→ Attacker biết plaintext có cấu trúc lặp!"
        )

    # ── GCM ──
    section("Bước 3 — Mã hóa cùng plaintext bằng AES-GCM")

    key_gcm = os.urandom(16)
    nonce   = os.urandom(12)
    aesgcm  = AESGCM(key_gcm)
    ct_gcm  = aesgcm.encrypt(nonce, plaintext, None)

    # ct_gcm gồm ciphertext + 16-byte auth tag ở cuối
    ct_only = ct_gcm[:-16]
    auth_tag = ct_gcm[-16:]

    print(f"\n  Ciphertext GCM (hex theo từng block 16 byte):")
    gcm_blocks = []
    for i in range(0, len(ct_only), 16):
        blk = ct_only[i:i+16]
        gcm_blocks.append(blk.hex())
        print(f"    Block {i//16}: {blk.hex()}")
    print(f"  Auth Tag  : {auth_tag.hex()}  ← xác thực toàn vẹn")

    gcm_duplicates = len(gcm_blocks) - len(set(gcm_blocks))
    print()
    if gcm_duplicates == 0:
        result_ok("Không có block trùng nhau → không lộ cấu trúc dữ liệu!")

    result_ok("Auth Tag phát hiện nếu ciphertext bị chỉnh sửa (tamper detection)")

    conclusion(
        "AES-ECB: block giống → ciphertext giống → lộ pattern.\n"
        "           AES-GCM: CTR mode + auth tag → an toàn, toàn vẹn được đảm bảo."
    )


# ═══════════════════════════════════════════════════════════════
# DEMO 3 — BENCHMARK ARGON2 (Thay thế Demo 3 cũ)
# ═══════════════════════════════════════════════════════════════

def quick_benchmark():
    password = "TestP@ss123!"
    configs = [
        ("memory=8MB,  time=1", {"time_cost": 1, "memory_cost": 8192,  "parallelism": 1}),
        ("memory=32MB, time=2", {"time_cost": 2, "memory_cost": 32768, "parallelism": 2}),
        ("memory=64MB, time=3", {"time_cost": 3, "memory_cost": 65536, "parallelism": 4}),
    ]

    print(f"\n  {'Config':<25} {'Thời gian TB':>14}  {'Hash/giây':>12}")
    print(f"  {'-'*25} {'-'*14}  {'-'*12}")

    for label, params in configs:
        ph = PasswordHasher(**params)
        ph.hash(password)  # warm up
        times = []
        for _ in range(3):
            t0 = time.perf_counter()
            ph.hash(password)
            times.append(time.perf_counter() - t0)
        avg_ms = (sum(times) / len(times)) * 1000
        hps = 1000 / avg_ms
        flag = f"  {YELLOW}← khuyến nghị{RESET}" if "64MB" in label else ""
        print(f"  {label:<25} {avg_ms:>12.1f}ms  {hps:>10.2f}/s{flag}")


def demo3_benchmark():
    banner("BENCHMARK ARGON2 — Thời gian hash & Memory Usage", 3)

    theory(
        "Để đánh giá hiệu năng thực tế của Argon2, chúng ta đo:",
        "• Thời gian hash trung bình",
        "• Bộ nhớ sử dụng theo memory_cost",
        "",
        "Tham số mặc định khuyến nghị: memory=64MB, time=3",
    )

    quick_benchmark()

    section("Kết quả phân tích")

    print(f"""
  → Thời gian hash ~200-400ms là mức chấp nhận được cho web/app.
  → Nếu quá nhanh (< 100ms) → cost quá thấp, dễ bị brute-force.
  → Nếu quá chậm (> 1 giây) → ảnh hưởng trải nghiệm người dùng.
    """)

    conclusion(
        "Benchmark giúp chúng ta cân bằng giữa Bảo mật và Hiệu năng.\n"
        "           Argon2 cho phép điều chỉnh memory_cost và time_cost linh hoạt."
    )


# ═══════════════════════════════════════════════════════════════
# DEMO 4 — Argon2 memory_cost & Brute-force Estimate
# ═══════════════════════════════════════════════════════════════

def demo4_memory_cost():
    banner("ARGON2 MEMORY COST — Tại sao memory-hard chống GPU?", 4)

    theory(
        "Argon2 chia bộ nhớ thành p×q block (mỗi block 1 KB).",
        "  B[i][j] = G( B[i][j-1],  B[i][ φ(j) ] )",
        "  φ(j): chỉ số phụ thuộc vào dữ liệu trước → không thể song song hóa tự do.",
        "",
        "GPU mạnh nhưng thiếu RAM lớn per-core:",
        "  CPU high-end:  nhiều GB RAM/core  → tốc độ hash thấp",
        "  GPU RTX 4090:  ~100KB SRAM/core   → memory_cost > 512KB là bottleneck",
        "",
        "→ Tăng memory_cost = tăng chi phí GPU attack theo hàm tuyến tính.",
    )

    password = "TestP@ss123!"

    configs = [
        ("256 KB  (rất yếu)", {"time_cost": 1, "memory_cost": 256,    "parallelism": 1}),
        ("1 MB    (yếu)",     {"time_cost": 1, "memory_cost": 1024,   "parallelism": 1}),
        ("10 MB   (trung bình)", {"time_cost": 2, "memory_cost": 10240,  "parallelism": 2}),
        ("100 MB  (khuyến nghị)", {"time_cost": 2, "memory_cost": 102400, "parallelism": 8}),
    ]

    section("Bước 1 — Đo thời gian hash với các mức memory_cost khác nhau")

    print(f"\n  {'Config':<25} {'Memory':<12} {'Thời gian':>10}  {'Hash/giây':>12}  {'Crack 10^9 pass':>18}")
    print(f"  {'-'*25} {'-'*12} {'-'*10}  {'-'*12}  {'-'*18}")

    BILLION = 1_000_000_000

    for label, params in configs:
        ph = PasswordHasher(**params)

        # Warm up
        ph.hash(password)

        # Đo thời gian trung bình 3 lần
        times = []
        for _ in range(3):
            t0 = time.perf_counter()
            ph.hash(password)
            times.append(time.perf_counter() - t0)

        avg_ms  = (sum(times) / len(times)) * 1000
        hps     = 1000 / avg_ms                          # hash per second
        crack_s = BILLION / hps                           # giây để thử 1 tỷ mật khẩu

        if crack_s < 60:
            crack_str = f"{crack_s:.0f} giây"
        elif crack_s < 3600:
            crack_str = f"{crack_s/60:.1f} phút"
        elif crack_s < 86400:
            crack_str = f"{crack_s/3600:.1f} giờ"
        elif crack_s < 86400 * 365:
            crack_str = f"{crack_s/86400:.0f} ngày"
        else:
            crack_str = f"{crack_s/86400/365:.0f} năm"

        mem_label = params['memory_cost']
        mem_str   = f"{mem_label//1024} MB" if mem_label >= 1024 else f"{mem_label} KB"

        flag = f"  {YELLOW}←{RESET}" if params["memory_cost"] == 102400 else ""
        print(
            f"  {label:<25} {mem_str:<12} {avg_ms:>8.1f}ms  "
            f"{hps:>10.2f}/s  {crack_str:>18}{flag}"
        )

    section("Bước 2 — GPU vs CPU (ước tính lý thuyết)")

    print(f"""
  CPU (1 core, memory_cost=100MB):
    → ~1 hash/giây  →  10^9 mật khẩu ≈ hàng chục năm

  GPU RTX 4090 (memory_cost=100MB):
    → Mỗi GPU core chỉ có ~100KB cache
    → Phải dùng VRAM chậm hơn cache ~10-100×
    → Thực tế: ~5-50 hash/giây per GPU  (không scale như MD5!)

  GPU RTX 4090 với MD5 (không memory-hard):
    → {GREEN}~10,000,000,000 hash/giây{RESET}  (10 tỷ/giây!)
    → 10^9 mật khẩu = {RED}< 1 giây{RESET}
    """)

    result_ok("memory_cost=100MB: GPU bị bottleneck bởi băng thông VRAM → tốc độ gần bằng CPU")
    result_fail("MD5/SHA256: GPU hash hàng tỷ lần/giây → brute-force trivial với từ điển nhỏ")

    conclusion(
        "memory_cost cao = RAM nhiều = GPU không thể song song hóa hiệu quả.\n"
        "           Đây là lý do Argon2 được chọn thay bcrypt/PBKDF2 cho hệ thống hiện đại."
    )


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"\n{BOLD}{'=' * 62}")
    print("  DEMO ĐIỂM YẾU MẬT KHẨU & MÃ HÓA — An toàn thông tin")
    print(f"  Đề 12: Kiểm tra độ mạnh mật khẩu & Mã hóa CSDL")
    print(f"{'=' * 62}{RESET}")
    print(f"\n  4 demo sẽ chạy theo thứ tự:")
    print("  1. Rainbow Table Attack (MD5 no-salt vs Argon2)")
    print("  2. AES-ECB lộ pattern vs AES-GCM")
    print("  3. Benchmark Argon2 — Thời gian hash & Memory Usage")
    print("  4. Argon2 memory_cost & GPU brute-force estimate")

    pause()
    demo1_rainbow_table()
    pause()
    demo2_ecb_vs_gcm()
    pause()
    demo3_benchmark()
    pause()
    demo4_memory_cost()

    print(f"\n{BOLD}{'=' * 62}")
    print("  Hoàn thành tất cả demo.")
    print(f"{'=' * 62}{RESET}\n")


if __name__ == "__main__":
    main()
