import os
from datetime import datetime
from contextlib import contextmanager
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

from modules.encryption import decrypt_value

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "password_security"),
    "charset": "utf8mb4",
    "use_unicode": True,
}


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        # If database does not exist, try to create it then reconnect
        if "Unknown database" in str(e):
            try:
                cfg = DB_CONFIG.copy()
                db_name = cfg.pop("database")
                conn0 = mysql.connector.connect(**cfg)
                cur = conn0.cursor()
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cur.close()
                conn0.close()
                conn = mysql.connector.connect(**DB_CONFIG)
                return conn
            except Exception as create_err:
                raise RuntimeError(f"Không thể kết nối hoặc tạo database: {create_err}") from e
        raise RuntimeError(f"Không thể kết nối MySQL: {e}")


@contextmanager
def get_cursor(commit: bool = False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
        if commit:
            conn.commit()
    finally:
        cursor.close()
        conn.close()


def init_db():
    """Create tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(20) UNIQUE NOT NULL,
                full_name TEXT,
                email TEXT,
                password_hash TEXT NOT NULL,
                phone TEXT,
                identify_card TEXT,
                address TEXT,
                failed_login_attempts INT DEFAULT 0,
                locked_until DATETIME NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # activity_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NULL,
                action VARCHAR(100) NOT NULL,
                details TEXT,
                ip_address VARCHAR(45) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_action (action),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        conn.commit()

        # --- Schema migration for existing old tables (add missing columns safely) ---
        # users columns we rely on
        expected_user_cols = [
            ("full_name", "TEXT"),
            ("email", "TEXT"),
            ("password_hash", "TEXT NOT NULL"),
            ("phone", "TEXT"),
            ("identify_card", "TEXT"),
            ("address", "TEXT"),
            ("failed_login_attempts", "INT DEFAULT 0"),
            ("locked_until", "DATETIME NULL"),
        ]
        for col_name, col_def in expected_user_cols:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
            except Error:
                pass  # column already exists or other harmless error

        # activity_logs basic columns
        expected_log_cols = [
            ("user_id", "INT NULL"),
            ("action", "VARCHAR(100) NOT NULL"),
            ("details", "TEXT"),
            ("ip_address", "VARCHAR(45) NULL"),
        ]
        for col_name, col_def in expected_log_cols:
            try:
                cursor.execute(f"ALTER TABLE activity_logs ADD COLUMN {col_name} {col_def}")
            except Error:
                pass

        conn.commit()
    finally:
        cursor.close()
        conn.close()


def _decrypt_user_row(row: dict | None) -> dict | None:
    """Decrypt sensitive columns in a user row returned from DB."""
    if not row:
        return None
    user = dict(row)
    user["full_name"] = decrypt_value(user.get("full_name"))
    user["email"] = decrypt_value(user.get("email"))
    user["phone"] = decrypt_value(user.get("phone"))
    user["identify_card"] = decrypt_value(user.get("identify_card"))
    user["address"] = decrypt_value(user.get("address"))
    # username and password_hash stay as-is (plaintext / hash)
    return user


def create_user(user_data: dict) -> int:
    """Insert new user. user_data must contain already-hashed and encrypted values where appropriate.
    Returns new user id.
    """
    sql = """
        INSERT INTO users (username, full_name, email, password_hash, phone, identify_card, address,
                           failed_login_attempts, locked_until)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (
            user_data["username"],
            user_data.get("full_name"),
            user_data.get("email"),
            user_data["password_hash"],
            user_data.get("phone"),
            user_data.get("identify_card"),
            user_data.get("address"),
            0,
            None,
        ))
        return cur.lastrowid


def get_user_by_id(user_id: int) -> dict | None:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        return _decrypt_user_row(row)


def get_user_by_username(username: str) -> dict | None:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        return _decrypt_user_row(row)


def get_all_users() -> list[dict]:
    """Used for email-based lookup (small dataset). Returns decrypted users."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        return [_decrypt_user_row(r) for r in rows if r]


def update_user_fields(user_id: int, fields: dict):
    """Generic update for allowed columns. fields keys must match column names.
    Values for sensitive fields should already be encrypted (or None).
    """
    if not fields:
        return
    allowed = {"full_name", "email", "phone", "identify_card", "address", "password_hash",
               "failed_login_attempts", "locked_until"}
    set_parts = []
    values = []
    for k, v in fields.items():
        if k in allowed:
            set_parts.append(f"{k} = %s")
            values.append(v)
    if not set_parts:
        return
    values.append(user_id)
    sql = f"UPDATE users SET {', '.join(set_parts)} WHERE id = %s"
    with get_cursor(commit=True) as cur:
        cur.execute(sql, values)


def increment_failed_attempts(user_id: int) -> int:
    """Increment and return new attempts count."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE id = %s",
            (user_id,)
        )
        cur.execute("SELECT failed_login_attempts FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        return row["failed_login_attempts"] if row else 0


def reset_failed_attempts(user_id: int):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE id = %s",
            (user_id,)
        )


def set_user_locked(user_id: int, locked_until: datetime):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE users SET locked_until = %s WHERE id = %s",
            (locked_until, user_id)
        )


def log_activity(user_id: int | None, action: str, details: str | None = None, ip_address: str | None = None):
    """Ghi log hoạt động vào DB.

    Hỗ trợ thêm ip_address (do logger.py cung cấp qua get_client_ip()).
    Tham số ip_address là optional để giữ tương thích ngược nếu có code gọi trực tiếp cũ.
    """
    sql = "INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (%s, %s, %s, %s)"
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (user_id, action, details, ip_address))
