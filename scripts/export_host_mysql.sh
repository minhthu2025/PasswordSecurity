#!/usr/bin/env bash
# Export MySQL trên máy host (port 3306) ra file seed cho service migrate Docker.
# Chạy TRÊN MÁY HOST trước `docker compose up` (macOS không cho container vào 127.0.0.1:3306).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/docker-migrate"
SEED_FILE="${OUT_DIR}/seed.sql"
META_FILE="${OUT_DIR}/meta.env"

# Đọc cấu hình từ .env nếu có
if [[ -f "${ROOT_DIR}/.env" ]]; then
  # shellcheck disable=SC1091
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

DB_HOST="${MIGRATE_SOURCE_HOST:-127.0.0.1}"
DB_PORT="${MIGRATE_SOURCE_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-password_security}"

mkdir -p "${OUT_DIR}"

if ! command -v mysqldump >/dev/null 2>&1; then
  echo "[export] Không tìm thấy mysqldump — bỏ qua export host."
  exit 0
fi

if ! mysql -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_PASSWORD}" \
  -e "USE \`${DB_NAME}\`;" >/dev/null 2>&1; then
  echo "[export] Không kết nối được MySQL host ${DB_HOST}:${DB_PORT} — bỏ qua export."
  exit 0
fi

echo "[export] Đang dump ${DB_NAME} từ host:${DB_PORT} → ${SEED_FILE}"

# Bỏ --routines/--triggers để tránh lỗi LIBRARIES khi client MySQL mới hơn server 8.0
mysqldump -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_PASSWORD}" \
  --single-transaction --no-tablespaces --column-statistics=0 \
  --skip-routines --skip-triggers \
  "${DB_NAME}" > "${SEED_FILE}"

USER_COUNT="$(mysql -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_PASSWORD}" \
  -N -e "SELECT COUNT(*) FROM users;" "${DB_NAME}")"

cat > "${META_FILE}" <<EOF
# Sinh tự động bởi export_host_mysql.sh — dùng cho migrate Docker
SOURCE_USER_COUNT=${USER_COUNT}
EOF

echo "[export] Hoàn tất: ${USER_COUNT} user → ${SEED_FILE}"