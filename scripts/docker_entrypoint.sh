#!/bin/sh
# Entrypoint Docker: khởi động giao diện Streamlit.
# (Migrate host→Docker chạy ở service `migrate` trong docker-compose.yml)
set -e

echo "[entrypoint] Khởi động PassGuard (Streamlit)..."
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0