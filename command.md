Command chạy chuẩn (copy paste dùng luôn):

# Build image (lần đầu hoặc sau khi thay đổi Dockerfile/requirements.txt)
docker compose build

# 1. Khởi động database chạy nền (detached)
docker compose up -d db

# 2. Chạy CLI tương tác (menu đầy đủ, gõ phím bình thường)
docker compose run --rm -it app

Nếu bạn muốn "chạy một phát là xong" (db nền + vào luôn CLI):

docker compose up -d db && docker compose run --rm -it app

Các lệnh hay dùng khác:

# Dừng database (khi không dùng nữa)
docker compose down

# Chạy lại CLI sau này (chỉ cần lệnh này là đủ, db sẽ tự có nếu đang tắt)
docker compose run --rm -it app

# Xem log database
docker compose logs -f db