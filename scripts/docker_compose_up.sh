#!/usr/bin/env bash
# Wrapper khởi động Docker: export MySQL host (3306) rồi chạy docker compose up.
# Dùng script này thay cho `docker compose up` để tự động migrate dữ liệu.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT_DIR}"

echo "[docker-up] Bước 1/2: export dữ liệu MySQL host (nếu có)..."
bash "${ROOT_DIR}/scripts/export_host_mysql.sh" || true

echo "[docker-up] Bước 2/2: khởi động Docker Compose..."
exec docker compose up "$@"