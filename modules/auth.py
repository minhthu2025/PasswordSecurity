from datetime import datetime, timedelta

from modules.database import (
    create_user,
    get_user_by_username,
    get_all_users,
    update_user_fields,
    increment_failed_attempts,
    reset_failed_attempts,
    set_user_locked,
    get_user_by_id,
)
from modules.encryption import encrypt_value
from modules.password_utils import (
    hash_password,
    verify_password,
    get_password_strength,
    meets_password_requirements,
    get_password_requirements_message,
    is_valid_username,
    is_valid_email,
    is_valid_phone,
    is_valid_identify_card,
)
from modules.logger import (
    log_activity,
    ACTION_REGISTER,
    ACTION_LOGIN_SUCCESS,
    ACTION_LOGIN_FAILED,
    ACTION_LOGIN_LOCKED,
    ACTION_UPDATE_PROFILE,
    ACTION_CHANGE_PASSWORD,
)


LOCK_DURATION_MINUTES = 3
MAX_FAILED_ATTEMPTS = 5


def _get_remaining_lock_time(locked_until: datetime) -> str:
    """Return human readable remaining time like '2 phút 15 giây'."""
    now = datetime.now()
    if locked_until <= now:
        return "0 giây"
    delta = locked_until - now
    total_seconds = int(delta.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    if minutes > 0:
        return f"{minutes} phút {seconds} giây"
    return f"{seconds} giây"


def register_user(
    username: str,
    full_name: str,
    email: str,
    password: str,
    confirm_password: str,
    phone: str | None = None,
    identify_card: str | None = None,
    address: str | None = None,
) -> tuple[bool, str, int | None]:
    """Validate and create user. Returns (success, message, user_id or None)."""
    # Username
    ok, msg = is_valid_username(username)
    if not ok:
        return False, msg, None

    if get_user_by_username(username):
        return False, "Username đã tồn tại. Vui lòng chọn username khác.", None

    # Email
    if not is_valid_email(email):
        return False, "Email không hợp lệ. Vui lòng nhập đúng định dạng (ví dụ: name@example.com).", None

    # Check email duplicate (decrypt all - small dataset)
    for u in get_all_users():
        if u and u.get("email") and u["email"].lower() == email.lower():
            return False, "Email này đã được sử dụng bởi tài khoản khác.", None

    # Password confirm
    if password != confirm_password:
        return False, "Mật khẩu xác nhận không khớp.", None

    # Strength
    if not meets_password_requirements(password):
        return False, get_password_requirements_message(), None

    strength = get_password_strength(password)

    # Optional fields validation
    if not is_valid_phone(phone):
        return False, "Số điện thoại không hợp lệ. Vui lòng nhập đúng 10 chữ số.", None
    if not is_valid_identify_card(identify_card):
        return False, "Số CMND/CCCD không hợp lệ. Vui lòng nhập đúng 12 chữ số.", None

    # Hash + encrypt
    password_hash = hash_password(password)
    enc_full_name = encrypt_value(full_name.strip())
    enc_email = encrypt_value(email.strip())
    enc_phone = encrypt_value(phone.strip() if phone else None)
    enc_identify = encrypt_value(identify_card.strip() if identify_card else None)
    enc_address = encrypt_value(address.strip() if address else None)

    user_data = {
        "username": username.strip(),
        "full_name": enc_full_name,
        "email": enc_email,
        "password_hash": password_hash,
        "phone": enc_phone,
        "identify_card": enc_identify,
        "address": enc_address,
    }

    try:
        user_id = create_user(user_data)
        log_activity(user_id, ACTION_REGISTER, f"Đăng ký thành công với username={username}, strength={strength}")
        return True, "Đăng ký tài khoản thành công!", user_id
    except Exception as e:
        return False, f"Lỗi khi tạo tài khoản: {e}", None


def login_user(identifier: str, password: str) -> tuple[bool, str, dict | None]:
    """Login with username or email. Returns (success, message, user_dict or None)."""
    # Find user (by username fast path, then email)
    user = get_user_by_username(identifier)
    if not user:
        # Try email lookup
        for u in get_all_users():
            if u and u.get("email") and u["email"].lower() == identifier.lower():
                user = u
                break

    if not user:
        return False, "Tài khoản không tồn tại.", None

    user_id = user["id"]

    # Check lock first (even if password correct later)
    locked_until = user.get("locked_until")
    if locked_until and locked_until > datetime.now():
        remaining = _get_remaining_lock_time(locked_until)
        log_activity(user_id, ACTION_LOGIN_LOCKED, f"Thử đăng nhập khi đang bị khóa. Còn {remaining}")
        return False, f"Tài khoản đang bị khóa do nhập sai mật khẩu 5 lần. Thời gian mở khóa còn lại: {remaining}.", None

    # If lock time passed, auto reset
    if locked_until and locked_until <= datetime.now():
        reset_failed_attempts(user_id)
        user["failed_login_attempts"] = 0
        user["locked_until"] = None

    # Verify password
    if not verify_password(password, user["password_hash"]):
        attempts = increment_failed_attempts(user_id)
        log_activity(user_id, ACTION_LOGIN_FAILED, f"Sai mật khẩu. Lần thử {attempts}/{MAX_FAILED_ATTEMPTS}")
        if attempts >= MAX_FAILED_ATTEMPTS:
            lock_time = datetime.now() + timedelta(minutes=LOCK_DURATION_MINUTES)
            set_user_locked(user_id, lock_time)
            remaining = _get_remaining_lock_time(lock_time)
            return False, f"Đăng nhập thất bại. Tài khoản đã bị khóa 3 phút do nhập sai 5 lần. Thời gian mở khóa còn lại: {remaining}.", None
        return False, f"Sai mật khẩu. Bạn còn {MAX_FAILED_ATTEMPTS - attempts} lần thử.", None

    # Success
    reset_failed_attempts(user_id)
    log_activity(user_id, ACTION_LOGIN_SUCCESS, f"Đăng nhập thành công (username={user.get('username')})")
    return True, "Đăng nhập thành công.", user


def get_user_profile(user_id: int) -> dict | None:
    return get_user_by_id(user_id)


def update_user_profile(
    user_id: int,
    full_name: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    identify_card: str | None = None,
    address: str | None = None,
) -> tuple[bool, str]:
    """Update profile fields. None/empty means keep current value.
    Returns (success, message).
    """
    current = get_user_by_id(user_id)
    if not current:
        return False, "Không tìm thấy tài khoản."

    # Prepare new values (use current if blank)
    new_full_name = (full_name.strip() if full_name and full_name.strip() else current.get("full_name"))
    new_email = (email.strip() if email and email.strip() else current.get("email"))
    new_phone = (phone.strip() if phone and phone.strip() else current.get("phone"))
    new_identify = (identify_card.strip() if identify_card and identify_card.strip() else current.get("identify_card"))
    new_address = (address.strip() if address and address.strip() else current.get("address"))

    # Validations (only if value changed / provided)
    if email and email.strip():
        if not is_valid_email(new_email):
            return False, "Email mới không hợp lệ."
        # Check duplicate email (exclude self)
        for u in get_all_users():
            if u and u["id"] != user_id and u.get("email") and u["email"].lower() == new_email.lower():
                return False, "Email này đã được sử dụng bởi tài khoản khác."

    if phone and phone.strip():
        if not is_valid_phone(new_phone):
            return False, "Số điện thoại mới không hợp lệ (phải đúng 10 chữ số)."

    if identify_card and identify_card.strip():
        if not is_valid_identify_card(new_identify):
            return False, "Số CMND/CCCD mới không hợp lệ (phải đúng 12 chữ số)."

    # Encrypt for storage
    fields = {
        "full_name": encrypt_value(new_full_name),
        "email": encrypt_value(new_email),
        "phone": encrypt_value(new_phone),
        "identify_card": encrypt_value(new_identify),
        "address": encrypt_value(new_address),
    }

    try:
        update_user_fields(user_id, fields)
        changed = []
        if new_full_name != current.get("full_name"):
            changed.append("full_name")
        if new_email != current.get("email"):
            changed.append("email")
        if new_phone != current.get("phone"):
            changed.append("phone")
        if new_identify != current.get("identify_card"):
            changed.append("identify_card")
        if new_address != current.get("address"):
            changed.append("address")
        log_activity(user_id, ACTION_UPDATE_PROFILE, f"Cập nhật: {', '.join(changed) if changed else 'không có thay đổi'}")
        return True, "Cập nhật thông tin thành công."
    except Exception as e:
        return False, f"Lỗi cập nhật: {e}"


def change_user_password(
    user_id: int,
    old_password: str,
    new_password: str,
    confirm_new_password: str,
) -> tuple[bool, str]:
    """Change password after verifying old one."""
    user = get_user_by_id(user_id)
    if not user:
        return False, "Không tìm thấy tài khoản."

    if not verify_password(old_password, user["password_hash"]):
        return False, "Mật khẩu cũ không đúng."

    if new_password != confirm_new_password:
        return False, "Mật khẩu mới và xác nhận không khớp."

    if not meets_password_requirements(new_password):
        return False, get_password_requirements_message()

    if verify_password(new_password, user["password_hash"]):
        return False, "Mật khẩu mới không được trùng với mật khẩu cũ."

    new_hash = hash_password(new_password)
    try:
        update_user_fields(user_id, {"password_hash": new_hash})
        # Also reset lock state on pw change success
        reset_failed_attempts(user_id)
        log_activity(user_id, ACTION_CHANGE_PASSWORD, "Thay đổi mật khẩu thành công")
        return True, "Đổi mật khẩu thành công."
    except Exception as e:
        return False, f"Lỗi đổi mật khẩu: {e}"
