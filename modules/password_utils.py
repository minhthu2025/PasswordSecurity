import re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

ph = PasswordHasher(
    time_cost=2,
    memory_cost=102400,  # 100 MiB
    parallelism=8,
    hash_len=32,
    salt_len=16,
)

FORBIDDEN_USERNAMES = [
    "admin", "root", "support", "administrator", "sysadmin", "moderator",
    "webmaster", "security", "password", "user", "test", "guest", "info",
    "contact", "help", "service", "system", "superuser", "manager"
]


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        ph.verify(password_hash, password)
        return True
    except (VerifyMismatchError, InvalidHashError):
        return False


def meets_password_requirements(password: str) -> bool:
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    return has_upper and has_lower and has_digit and has_special


def get_password_strength(password: str) -> str:
    """Return 'Weak' | 'Medium' | 'Strong'.
    Weak   = < 8 ký tự hoặc thiếu yêu cầu bắt buộc.
    Medium = đủ yêu cầu, 8–11 ký tự.
    Strong = đủ yêu cầu, >= 12 ký tự.
    """
    if not meets_password_requirements(password):
        return "Weak"
    if len(password) < 12:
        return "Medium"
    return "Strong"


# Bản tiếng Việt — dùng cho hiển thị giao diện và test_bulk_passwords.py
_STRENGTH_VI = {"Weak": "Yếu", "Medium": "Trung bình", "Strong": "Mạnh"}

def check_password_strength(password: str) -> str:
    """Trả về độ mạnh mật khẩu bằng tiếng Việt: 'Yếu' | 'Trung bình' | 'Mạnh'."""
    return _STRENGTH_VI[get_password_strength(password)]


def get_password_requirements_message() -> str:
    return "Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt."


def is_valid_username(username: str) -> tuple[bool, str]:
    if not (6 <= len(username) <= 20):
        return False, "Username phải có độ dài từ 6 đến 20 ký tự."

    if not re.match(r"^[a-zA-Z0-9._-]+$", username):
        return False, "Username chỉ được chứa chữ cái (hoa/thường), số, dấu chấm (.), gạch ngang (-) và gạch dưới (_)."

    lower = username.lower()
    for bad in FORBIDDEN_USERNAMES:
        if bad in lower:
            return False, f"Username không được chứa từ cấm '{bad}'."

    return True, ""


def is_valid_email(email: str) -> bool:
    if not email or "@" not in email:
        return False
    # Simple but effective regex for most cases
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def is_valid_phone(phone: str | None) -> bool:
    if phone is None or phone == "":
        return True  # optional
    # Must be exactly 10 digits after stripping non-digits? Per spec: 10 số
    digits = "".join(filter(str.isdigit, phone))
    return len(digits) == 10 and len(phone) == 10  # require pure 10 digits, no extra chars


def is_valid_identify_card(identify_card: str | None) -> bool:
    if identify_card is None or identify_card == "":
        return True  # optional
    digits = "".join(filter(str.isdigit, identify_card))
    return len(digits) == 12 and len(identify_card) == 12


def password_input(label: str, key: str, placeholder: str = "") -> str:
    """Ô mật khẩu native — type=password, không dùng nested columns."""
    import streamlit as st

    value = st.text_input(
        label,
        type="password",
        key=key,
        placeholder=placeholder,
    )
    return value or ""
