#!/usr/bin/env python3
"""
Migrate dữ liệu MySQL từ máy host sang MySQL container Docker.

Hai chế độ (theo thứ tự ưu tiên):
1. Import file SQL do scripts/export_host_mysql.sh tạo (khuyến nghị trên macOS).
2. Copy trực tiếp qua kết nối TCP (hoạt động tốt trên Linux khi MySQL host cho phép).

Chỉ đồng bộ khi DB Docker có ít user hơn nguồn (trừ khi MIGRATE_FORCE=1).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Thêm thư mục gốc dự án vào sys.path để import modules.*
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import mysql.connector
from mysql.connector import Error

from modules.database import init_db

# Bảng cần đồng bộ (bảng cha trước khi INSERT; bảng con trước khi TRUNCATE)
TABLES_PARENT_FIRST = ("users", "activity_logs")


def _env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _db_config(host: str, port: int) -> dict:
    return {
        "host": host,
        "port": port,
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "password_security"),
        "charset": "utf8mb4",
        "use_unicode": True,
    }


def _connect(cfg: dict) -> tuple:
    """Kết nối MySQL; trả về (connection, None) hoặc (None, lỗi)."""
    try:
        return mysql.connector.connect(**cfg), None
    except Error as exc:
        return None, exc


def _count_rows(conn, table: str) -> int:
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        return int(cur.fetchone()[0])
    finally:
        cur.close()


def _load_source_user_count_from_meta(meta_path: Path) -> int | None:
    """Đọc SOURCE_USER_COUNT từ docker-migrate/meta.env."""
    if not meta_path.is_file():
        return None
    for line in meta_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("SOURCE_USER_COUNT="):
            try:
                return int(line.split("=", 1)[1].strip())
            except ValueError:
                return None
    return None


def _truncate_tables(conn) -> None:
    cur = conn.cursor()
    try:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in reversed(TABLES_PARENT_FIRST):
            cur.execute(f"TRUNCATE TABLE `{table}`")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
    finally:
        cur.close()


def _copy_table(source_conn, target_conn, table: str) -> int:
    src_cur = source_conn.cursor(dictionary=True)
    tgt_cur = target_conn.cursor()
    try:
        src_cur.execute(f"SELECT * FROM `{table}`")
        rows = src_cur.fetchall()
        if not rows:
            return 0

        columns = list(rows[0].keys())
        col_sql = ", ".join(f"`{c}`" for c in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"INSERT INTO `{table}` ({col_sql}) VALUES ({placeholders})"
        values = [tuple(row[c] for c in columns) for row in rows]
        tgt_cur.executemany(insert_sql, values)
        target_conn.commit()
        return len(rows)
    finally:
        src_cur.close()
        tgt_cur.close()


def _import_sql_file(target_cfg: dict, sql_path: Path) -> int:
    """Import file .sql vào DB Docker bằng mysql client trong container."""
    env = os.environ.copy()
    if target_cfg.get("password"):
        env["MYSQL_PWD"] = str(target_cfg["password"])

    cmd = [
        "mysql",
        "-h",
        str(target_cfg["host"]),
        "-P",
        str(target_cfg["port"]),
        "-u",
        str(target_cfg["user"]),
        str(target_cfg["database"]),
    ]
    with sql_path.open("r", encoding="utf-8") as sql_file:
        subprocess.run(cmd, stdin=sql_file, env=env, check=True)
    return 0


def _should_migrate(source_users: int, target_users: int, force: bool) -> bool:
    if source_users == 0:
        print("[migrate] Nguồn không có user — không có gì để đồng bộ.")
        return False
    if not force and target_users >= source_users:
        print("[migrate] DB Docker đã đủ dữ liệu — bỏ qua đồng bộ.")
        return False
    return True


def _migrate_from_seed_file(target_cfg: dict) -> int | None:
    """
    Import từ docker-migrate/seed.sql (tạo bởi export_host_mysql.sh trên host).
    Trả về mã exit (0/1) nếu đã xử lý; None nếu không có file seed.
    """
    sql_path = Path(os.getenv("MIGRATE_SQL_FILE", "/migrate/seed.sql"))
    meta_path = Path(os.getenv("MIGRATE_META_FILE", "/migrate/meta.env"))

    if not sql_path.is_file():
        return None

    target_conn, target_err = _connect(target_cfg)
    if target_conn is None:
        print(f"[migrate] Không kết nối DB Docker để import SQL: {target_err}")
        return 1

    try:
        init_db()
        target_users = _count_rows(target_conn, "users")
        source_users = _load_source_user_count_from_meta(meta_path)
        if source_users is None:
            source_users = target_users + 1  # không có meta → vẫn thử import
        force = _env_flag("MIGRATE_FORCE", "0")

        print(
            f"[migrate] seed.sql — host: {source_users}, docker: {target_users}, "
            f"force={force}"
        )

        if not _should_migrate(source_users, target_users, force):
            return 0

        print(f"[migrate] Import {sql_path} → DB Docker...")
        target_conn.close()
        target_conn = None
        _import_sql_file(target_cfg, sql_path)
        print("[migrate] Import seed.sql hoàn tất.")
        return 0
    except Exception as exc:
        print(f"[migrate] Lỗi import seed.sql: {exc}")
        return 1
    finally:
        if target_conn is not None:
            target_conn.close()


def _migrate_live_copy(target_cfg: dict) -> int:
    """Copy trực tiếp host:3306 → DB Docker (Linux / MySQL bind 0.0.0.0)."""
    source_host = os.getenv("MIGRATE_SOURCE_HOST", "127.0.0.1")
    source_port = int(os.getenv("MIGRATE_SOURCE_PORT", "3306"))
    source_cfg = _db_config(source_host, source_port)

    source_conn, source_err = _connect(source_cfg)
    if source_conn is None:
        print(
            f"[migrate] Không kết nối MySQL host "
            f"({source_host}:{source_port}) — bỏ qua: {source_err}"
        )
        return 0

    target_conn, target_err = _connect(target_cfg)
    if target_conn is None:
        print(f"[migrate] Không kết nối DB Docker — lỗi: {target_err}")
        source_conn.close()
        return 1

    try:
        init_db()
        source_users = _count_rows(source_conn, "users")
        target_users = _count_rows(target_conn, "users")
        force = _env_flag("MIGRATE_FORCE", "0")

        print(
            f"[migrate] live copy — host: {source_users}, docker: {target_users}, "
            f"force={force}"
        )

        if not _should_migrate(source_users, target_users, force):
            return 0

        print("[migrate] Bắt đầu copy trực tiếp host → Docker...")
        _truncate_tables(target_conn)

        copied_total = 0
        for table in TABLES_PARENT_FIRST:
            n = _copy_table(source_conn, target_conn, table)
            copied_total += n
            print(f"[migrate]   • {table}: {n} dòng")

        print(f"[migrate] Hoàn tất — đã đồng bộ {copied_total} dòng.")
        return 0
    except Exception as exc:
        print(f"[migrate] Lỗi khi copy trực tiếp: {exc}")
        return 1
    finally:
        source_conn.close()
        target_conn.close()


def migrate_host_to_docker() -> int:
    """Trả về 0 nếu thành công hoặc bỏ qua; 1 nếu lỗi nghiêm trọng."""
    if not _env_flag("AUTO_MIGRATE_FROM_HOST", "0"):
        print("[migrate] AUTO_MIGRATE_FROM_HOST tắt — bỏ qua đồng bộ.")
        return 0

    # Đích: service migrate kết nối container `db` (không qua port 3307)
    target_cfg = _db_config(
        os.getenv("DB_HOST", "db"),
        int(os.getenv("DB_PORT", "3306")),
    )

    # Ưu tiên import file seed (macOS / MySQL chỉ listen localhost)
    seed_result = _migrate_from_seed_file(target_cfg)
    if seed_result is not None:
        return seed_result

    # Fallback: copy trực tiếp (Linux)
    return _migrate_live_copy(target_cfg)


if __name__ == "__main__":
    raise SystemExit(migrate_host_to_docker())