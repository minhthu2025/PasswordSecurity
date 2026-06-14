FROM python:3.12-slim

# Giảm buffering output (quan trọng cho CLI tương tác + log Docker)
# Không ghi .pyc bên trong container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Cài dependencies trước (tận dụng layer cache khi chỉ sửa code)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source (được .dockerignore lọc: loại venv, __pycache__, .env, logs, v.v.)
COPY . .

# Ứng dụng CLI tương tác.
# Chạy bằng: docker compose run --rm -it app
# (tty + stdin_open đã được cấu hình trong docker-compose.yml)
CMD ["python", "-u", "main.py"]
