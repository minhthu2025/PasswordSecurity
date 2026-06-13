FROM python:3.12-slim

WORKDIR /app

# Cài dependencies Python (không cache để image nhỏ)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code (trừ những gì trong .dockerignore)
COPY . .

# Chạy ứng dụng CLI chính
CMD ["python", "main.py"]
