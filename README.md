# Yêu cầu:
- python 3.10 trở lên (Nên cài trên ubuntu 22.04 trở lên, đã có sẵn python 3.10 +)
- Redis
  > sudo apt install redis -y

  > systemctl enable --now redis

  > redis-cli ping  (Kết quả trả ra PONG là ok)

# Cài đặt
> git clone https://github.com/KiritoU/truyenfull_manager.git

> Copy file .env vào folder truyenfull_manager

> python3 -m venv venv

> source venv/bin/activate

> pip install -r requirements.txt

# Chạy server

## Chạy web
> tmux new -s manager (hoặc tmux a -t manager nếu đã có session tmux tên manager)

> cd truyenfull_manager

> source venv/bin/activate

> python manage.py migrate

> daphne -b 0.0.0.0 -p 8000 core.asgi:application

> Ctrl+B D (Ẩn session tmux)

NOTE: Có thể thay đổi bind IP và port nếu có nhu cầu (khi thay đổi cần cập nhật bên tool crawl)

## Chạy celery worker (Mục đích: Update trạng thái truyện mà ko ảnh hưởng tới tốc độ truy cập web)
> tmux new -s manager_celery (hoặc tmux a -t manager_celery nếu đã có session tmux tên manager_celery)

> cd truyenfull_manager

> source venv/bin/activate

> celery -A core worker -l info

> Ctrl+B D (Ẩn session tmux)

## Chạy cron (Mục đích: Update trạng thái truyện đã crawl trên web 10s/lần mà ko cần reload web)
> tmux new -s manager_cron (hoặc tmux a -t manager_cron nếu đã có session tmux tên manager_cron)

> cd truyenfull_manager

> source venv/bin/activate

> python cron.py

> Ctrl+B D (Ẩn session tmux)

# Tham khảo:
- Deploy: https://channels.readthedocs.io/en/latest/deploying.html
- tmux: https://tmuxcheatsheet.com/
