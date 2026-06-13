import os
import base64
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# Tải biến môi trường từ file .env
load_dotenv()


def _load_master_key() -> bytes:
    """Đọc key mã hóa từ .env.

    Hỗ trợ 2 định dạng để tránh phá vỡ khi nâng cấp:

    1. MASTER_KEY (khuyến nghị): dạng hex 64 ký tự (32 bytes) - ví dụ: d782e2e8...
    2. ENCRYPTION_KEY (cũ, legacy): dạng base64 44 ký tự

    Nếu đang dùng key cũ sẽ in cảnh báo rõ ràng và hướng dẫn chuyển đổi.
    Nếu không có key nào hợp lệ sẽ raise lỗi với hướng dẫn cụ thể.
    """
    master_key = os.getenv("MASTER_KEY")
    legacy_key = os.getenv("ENCRYPTION_KEY")

    # Ưu tiên MASTER_KEY mới
    if master_key:
        key_hex = master_key.strip()
        try:
            key = bytes.fromhex(key_hex)
            if len(key) != 32:
                raise ValueError("MASTER_KEY phải có đúng 32 bytes (64 ký tự hex).")
            return key
        except Exception as e:
            raise ValueError(f"MASTER_KEY không hợp lệ (cần 64 ký tự hex): {e}")

    # Fallback cho key cũ (ENCRYPTION_KEY base64) - vẫn hoạt động nhưng cảnh báo
    if legacy_key:
        print("\n" + "=" * 70)
        print("⚠️  CẢNH BÁO: Bạn đang sử dụng ENCRYPTION_KEY (định dạng base64) cũ.")
        print("   Code hiện đã chuyển sang dùng MASTER_KEY (hex) để nhất quán hơn.")
        print("   Ứng dụng vẫn chạy được nhờ chế độ tương thích ngược.")
        print()
        print("   Khuyến nghị chuyển sang MASTER_KEY ngay để tránh lỗi sau này:")
        print()
        print("   Chạy lệnh sau để lấy giá trị MASTER_KEY tương đương:")
        print('   python -c "')
        print('   import os, base64')
        print('   from dotenv import load_dotenv; load_dotenv()')
        print('   k = base64.b64decode(os.getenv(\"ENCRYPTION_KEY\"))')
        print('   print(\"MASTER_KEY=\" + k.hex())')
        print('   "')
        print()
        print("   Sau đó thêm dòng MASTER_KEY=... vào file .env")
        print("   và xóa (hoặc comment) dòng ENCRYPTION_KEY cũ.")
        print("=" * 70 + "\n")

        try:
            key = base64.b64decode(legacy_key.strip())
            if len(key) != 32:
                raise ValueError("ENCRYPTION_KEY phải giải mã thành đúng 32 bytes.")
            return key
        except Exception as e:
            raise ValueError(f"ENCRYPTION_KEY cũ không hợp lệ: {e}")

    # Không có key nào
    raise ValueError(
        "MASTER_KEY chưa được thiết lập trong file .env. "
        "Tạo mới bằng: python -c \"import os; print(os.urandom(32).hex())\" "
        "rồi thêm vào .env: MASTER_KEY=<64 ký tự hex>"
    )


def encrypt_data(plaintext: str | None) -> str | None:
    """Mã hóa chuỗi plaintext bằng AES-GCM (AES-256).

    Quy trình:
    - Lấy key từ MASTER_KEY (hex -> bytes)
    - Sinh nonce ngẫu nhiên 12 byte
    - Mã hóa, kết hợp nonce + ciphertext
    - Trả về base64 để lưu dễ dàng trong TEXT/VARCHAR

    Trả về None nếu plaintext None hoặc rỗng.
    """
    if plaintext is None or plaintext == "":
        return None

    key = _load_master_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    try:
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        # Lưu nonce cùng với ciphertext để dùng khi giải mã
        return base64.b64encode(nonce + ciphertext).decode("ascii")
    except Exception as e:
        raise RuntimeError(f"Không thể mã hóa dữ liệu: {e}") from e


def decrypt_data(ciphertext: str | None) -> str | None:
    """Giải mã dữ liệu được tạo bởi encrypt_data.

    - Tách 12 byte nonce + phần ciphertext
    - Giải mã và xác thực bằng AESGCM (kiểm tra tag)
    - Trả về plaintext utf-8

    Trả về None (không raise) khi:
    - Input rỗng/None
    - Dữ liệu bị thay đổi (InvalidTag - sai key hoặc đã bị tamper)
    - Định dạng base64 hoặc độ dài không hợp lệ
    """
    if ciphertext is None or ciphertext == "":
        return None

    key = _load_master_key()
    try:
        data = base64.b64decode(ciphertext)
        if len(data) < 12:
            return None
        nonce, ct = data[:12], data[12:]
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ct, None)
        return plaintext.decode("utf-8")
    except (InvalidTag, ValueError, TypeError):
        # Sai key, dữ liệu hỏng, hoặc lỗi giải mã -> không crash, trả None
        return None


# --- Tương thích ngược ---
# Các file khác vẫn đang dùng encrypt_value / decrypt_value.
# Alias để không phá vỡ import hiện tại, đồng thời cung cấp encrypt_data / decrypt_data theo yêu cầu.
encrypt_value = encrypt_data
decrypt_value = decrypt_data
