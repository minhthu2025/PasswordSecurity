FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

COPY requirements.txt .
# mysql client: dùng import file seed.sql trong service migrate
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-mysql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn dự án (lọc qua .dockerignore)
COPY . .

EXPOSE 8501

# Script migrate (service `migrate`) + entrypoint Streamlit (service `app`)
COPY scripts/docker_entrypoint.sh /app/scripts/docker_entrypoint.sh
COPY scripts/migrate_host_mysql.py /app/scripts/migrate_host_mysql.py
RUN chmod +x /app/scripts/docker_entrypoint.sh

ENTRYPOINT ["/app/scripts/docker_entrypoint.sh"]