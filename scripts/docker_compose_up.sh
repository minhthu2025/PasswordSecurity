#!/usr/bin/env bash
# Wrapper khởi động Docker: export MySQL host (3306) rồi chạy docker compose up.
# Dùng script này thay cho `docker compose up` để tự động migrate dữ liệu.
#
# Chế độ mặc định: MySQL container (port 3307) + migrate + app.
# Nếu MySQL container bị OOM trên Docker Desktop: DOCKER_USE_HOST_DB=1

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT_DIR}"

USE_HOST_DB="${DOCKER_USE_HOST_DB:-0}"
HAS_BUILD=0
HAS_DETACH=0
EXTRA_ARGS=()

for arg in "$@"; do
  case "${arg}" in
    --build) HAS_BUILD=1 ;;
    -d|--detach) HAS_DETACH=1 ;;
    *) EXTRA_ARGS+=("${arg}") ;;
  esac
done

if [[ "${USE_HOST_DB}" == "1" ]]; then
  echo "[docker-up] Chế độ MySQL host: app → host.docker.internal:3306 (bỏ qua db/migrate)"
  export APP_DB_HOST=host.docker.internal
  export APP_DB_PORT=3306
  if (( HAS_BUILD )); then
    docker compose build app
  fi
  if (( HAS_DETACH )); then
    if ((${#EXTRA_ARGS[@]})); then
      docker compose up -d --no-deps app "${EXTRA_ARGS[@]}"
    else
      docker compose up -d --no-deps app
    fi
  else
    if ((${#EXTRA_ARGS[@]})); then
      docker compose up --no-deps app "${EXTRA_ARGS[@]}"
    else
      docker compose up --no-deps app
    fi
  fi
  exit 0
fi

echo "[docker-up] Bước 1/3: export dữ liệu MySQL host (nếu có)..."
bash "${ROOT_DIR}/scripts/export_host_mysql.sh" || true

export APP_DB_HOST=db
export APP_DB_PORT=3306

echo "[docker-up] Bước 2/3: khởi động MySQL container trước (tránh OOM khi build image song song)..."
docker compose up -d db

health="none"
deadline=$((SECONDS + 600))
reset_done=0

while (( SECONDS < deadline )); do
  status="$(docker inspect passwordsecurity-db --format '{{.State.Status}}' 2>/dev/null || echo missing)"
  health="$(docker inspect passwordsecurity-db --format '{{.State.Health.Status}}' 2>/dev/null || echo none)"
  restarts="$(docker inspect passwordsecurity-db --format '{{.RestartCount}}' 2>/dev/null || echo 0)"
  oom="$(docker inspect passwordsecurity-db --format '{{.State.OOMKilled}}' 2>/dev/null || echo false)"

  if [[ "${health}" == "healthy" ]]; then
    echo "[docker-up] MySQL container healthy."
    break
  fi

  if [[ "${reset_done}" == "0" ]] && { [[ "${oom}" == "true" ]] || (( restarts >= 1 )); }; then
    if docker compose logs db 2>/dev/null | grep -qE 'Unable to start server|initialize-insecure.*Killed|Killed'; then
      echo "[docker-up] Volume MySQL có thể hỏng (init bị kill/OOM) — reset volume và thử lại..."
      docker compose down -v
      docker compose up -d db
      reset_done=1
      deadline=$((SECONDS + 600))
    fi
  fi

  echo "[docker-up] Chờ MySQL... status=${status} health=${health} restarts=${restarts} oom=${oom}"
  sleep 15
done

if [[ "${health}" != "healthy" ]]; then
  echo "[docker-up] LỖI: MySQL container không healthy sau 10 phút."
  echo "[docker-up] Thường do Docker Desktop thiếu RAM (process init bị OOM kill)."
  echo "[docker-up] Thử một trong các cách sau:"
  echo "  • Tăng RAM Docker Desktop lên >= 6GB (Settings → Resources → Memory)"
  echo "  • docker compose down -v && bash scripts/docker_compose_up.sh --build"
  echo "  • Dùng MySQL trên máy: DOCKER_USE_HOST_DB=1 bash scripts/docker_compose_up.sh --build"
  exit 1
fi

echo "[docker-up] Bước 3/3: build (nếu có) và khởi động migrate + app..."
if (( HAS_BUILD )); then
  docker compose build migrate app
fi

if (( HAS_DETACH )); then
  if ((${#EXTRA_ARGS[@]})); then
    docker compose up -d migrate app "${EXTRA_ARGS[@]}"
  else
    docker compose up -d migrate app
  fi
else
  if ((${#EXTRA_ARGS[@]})); then
    docker compose up migrate app "${EXTRA_ARGS[@]}"
  else
    docker compose up migrate app
  fi
fi