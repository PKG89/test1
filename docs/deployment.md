# Развертывание

Руководство по развертыванию DXF Геообработка Бота в продакшен среде с использованием Docker, VPS и систем мониторинга.

## Содержание

- [Docker развертывание](#docker-развертывание)
- [VPS развертывание](#vps-развертывание)
- [Конфигурация переменных окружения](#конфигурация-переменных-окружения)
- [Логирование](#логирование)
- [Мониторинг](#мониторинг)
- [Резервное копирование](#резервное-копирование)
- [Масштабирование](#масштабирование)
- [Безопасность](#безопасность)

## Docker развертывание

### Создание Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание необходимых директорий
RUN mkdir -p templates output temp logs data

# Переменные окружения по умолчанию
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Запуск приложения
CMD ["python", "bot.py"]
```

### Оптимизированный многоэтапный Dockerfile

```dockerfile
# Dockerfile.multi-stage
FROM python:3.10-slim as builder

RUN apt-get update && apt-get install -y \
    gdal-bin libgdal-dev build-essential

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Финальный образ
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    gdal-bin libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование установленных пакетов
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .
RUN mkdir -p templates output temp logs data

ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

CMD ["python", "bot.py"]
```

### Docker Compose конфигурация

```yaml
# docker-compose.yml
version: '3.8'

services:
  bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dxf-geobot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./templates:/app/templates:ro
      - ./output:/app/output
      - ./logs:/app/logs
      - ./temp:/app/temp
    networks:
      - geobot-network
    depends_on:
      - redis
      - postgres
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  redis:
    image: redis:7-alpine
    container_name: geobot-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - geobot-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  postgres:
    image: postgres:15-alpine
    container_name: geobot-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME:-geobot}
      POSTGRES_USER: ${DB_USER:-geobot}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - geobot-network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  nginx:
    image: nginx:alpine
    container_name: geobot-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./output:/usr/share/nginx/html/output:ro
    networks:
      - geobot-network
    depends_on:
      - bot

  prometheus:
    image: prom/prometheus:latest
    container_name: geobot-prometheus
    restart: unless-stopped
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - geobot-network
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    container_name: geobot-grafana
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    networks:
      - geobot-network
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

volumes:
  redis-data:
  postgres-data:
  prometheus-data:
  grafana-data:

networks:
  geobot-network:
    driver: bridge
```

### Команды Docker

```bash
# Сборка образа
docker-compose build

# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Перезапуск конкретного сервиса
docker-compose restart bot

# Обновление образов
docker-compose pull
docker-compose up -d

# Масштабирование (если поддерживается)
docker-compose up -d --scale bot=3
```

## VPS развертывание

### Выбор VPS провайдера

**Рекомендуемые провайдеры:**

| Провайдер | Цена/месяц | RAM | CPU | Примечания |
|-----------|-----------|-----|-----|------------|
| Hetzner Cloud | от 5€ | 4GB | 2 | Отличное соотношение цена/качество |
| DigitalOcean | от $6 | 2GB | 1 | Простой в использовании |
| Vultr | от $6 | 2GB | 1 | Множество локаций |
| AWS EC2 | от $10 | 4GB | 2 | Гибкая настройка |
| VScale (RU) | от 300₽ | 2GB | 1 | Российский провайдер |

**Минимальные требования:**
- 2 GB RAM
- 2 CPU cores
- 20 GB SSD
- Ubuntu 22.04 LTS

### Пошаговое развертывание на Ubuntu VPS

#### Шаг 1: Начальная настройка сервера

```bash
# Подключение к серверу
ssh root@your_server_ip

# Обновление системы
apt update && apt upgrade -y

# Установка базовых пакетов
apt install -y curl git vim ufw fail2ban

# Создание пользователя для приложения
adduser geobot
usermod -aG sudo geobot

# Настройка SSH ключа (на локальной машине)
ssh-copy-id geobot@your_server_ip
```

#### Шаг 2: Настройка firewall

```bash
# Настройка UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Проверка статуса
ufw status
```

#### Шаг 3: Установка Docker

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Добавление пользователя в группу docker
usermod -aG docker geobot

# Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Проверка установки
docker --version
docker-compose --version
```

#### Шаг 4: Клонирование и настройка проекта

```bash
# Переключение на пользователя geobot
su - geobot

# Клонирование репозитория
git clone https://github.com/your-repo/dxf-geobot.git
cd dxf-geobot

# Создание .env файла
cp .env.example .env
nano .env

# Заполнить все необходимые переменные!
```

#### Шаг 5: Запуск приложения

```bash
# Сборка и запуск
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f bot
```

#### Шаг 6: Настройка Nginx (если не используется Docker Nginx)

```bash
# Установка Nginx
sudo apt install -y nginx

# Создание конфигурации
sudo nano /etc/nginx/sites-available/geobot
```

```nginx
# /etc/nginx/sites-available/geobot

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Раздача статических файлов (output DXF)
    location /output/ {
        alias /home/geobot/dxf-geobot/output/;
        autoindex off;
        expires 1h;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Метрики (защищены аутентификацией)
    location /metrics {
        auth_basic "Metrics";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://localhost:9090;
    }
}
```

```bash
# Активация конфигурации
sudo ln -s /etc/nginx/sites-available/geobot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Шаг 7: Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo certbot renew --dry-run

# Добавить в cron для автообновления
sudo crontab -e
# Добавить строку:
0 3 * * * certbot renew --quiet
```

#### Шаг 8: Настройка автозапуска

```bash
# Создание systemd service (альтернатива docker-compose)
sudo nano /etc/systemd/system/geobot.service
```

```ini
[Unit]
Description=DXF GeoBot Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/geobot/dxf-geobot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=geobot
Group=geobot

[Install]
WantedBy=multi-user.target
```

```bash
# Активация сервиса
sudo systemctl enable geobot
sudo systemctl start geobot
sudo systemctl status geobot
```

## Конфигурация переменных окружения

### Полный пример .env файла

```env
# ============================================
# ОСНОВНЫЕ НАСТРОЙКИ БОТА
# ============================================

# Telegram Bot Token (получить у @BotFather)
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Имя бота (без @)
BOT_USERNAME=dxf_geobot

# Режим работы (development, production)
ENVIRONMENT=production

# Язык по умолчанию
DEFAULT_LANGUAGE=ru

# ============================================
# НАСТРОЙКИ ОБРАБОТКИ ДАННЫХ
# ============================================

# Максимальное количество точек для обработки
MAX_POINTS=1000000

# Масштаб по умолчанию
DEFAULT_SCALE=1000

# Метод построения TIN (delaunay, constrained)
TIN_METHOD=delaunay

# Максимальная длина ребра TIN (метры, 0 = без ограничения)
MAX_EDGE_LENGTH=50

# Коэффициент денсификации по умолчанию
DENSIFY_FACTOR=2.0

# Метод интерполяции (linear, cubic, nearest)
INTERPOLATION_METHOD=linear

# ============================================
# ПУТИ К ФАЙЛАМ И ДИРЕКТОРИЯМ
# ============================================

# Директория с шаблонами DXF
TEMPLATES_DIR=./templates

# Директория для выходных файлов
OUTPUT_DIR=./output

# Временная директория
TEMP_DIR=./temp

# Директория с логами
LOGS_DIR=./logs

# Директория для данных
DATA_DIR=./data

# ============================================
# БАЗА ДАННЫХ (PostgreSQL)
# ============================================

# URL подключения к базе данных
DATABASE_URL=postgresql://geobot:password@postgres:5432/geobot

# Или отдельные параметры
DB_HOST=postgres
DB_PORT=5432
DB_NAME=geobot
DB_USER=geobot
DB_PASSWORD=secure_password_here

# Пул соединений
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# ============================================
# REDIS (для очередей и кэша)
# ============================================

REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=50

# TTL кэша (секунды)
CACHE_TTL=3600

# ============================================
# НАСТРОЙКИ БЕЗОПАСНОСТИ
# ============================================

# Список разрешенных пользователей (Telegram ID через запятую)
# Пустой = доступ для всех
ALLOWED_USERS=

# Список администраторов (Telegram ID)
ADMIN_USERS=123456789,987654321

# Максимальный размер загружаемого файла (MB)
MAX_FILE_SIZE=50

# Максимальное время обработки (секунды)
MAX_PROCESSING_TIME=300

# Секретный ключ для подписи токенов
SECRET_KEY=your_secret_key_here_change_in_production

# ============================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# ============================================

# Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Формат логов (text, json)
LOG_FORMAT=json

# Ротация логов
LOG_ROTATION=10 MB
LOG_RETENTION=30 days

# Логирование в файл
LOG_TO_FILE=true

# Логирование в консоль
LOG_TO_CONSOLE=true

# ============================================
# РАБОЧИЕ НАСТРОЙКИ
# ============================================

# Количество воркеров для обработки
WORKERS=4

# Таймаут операций (секунды)
TIMEOUT=300

# Размер очереди задач
QUEUE_SIZE=100

# ============================================
# МОНИТОРИНГ И МЕТРИКИ
# ============================================

# Sentry DSN для отслеживания ошибок
SENTRY_DSN=https://your_sentry_dsn_here

# Prometheus метрики
ENABLE_METRICS=true
METRICS_PORT=8000

# Healthcheck endpoint
HEALTHCHECK_ENABLED=true
HEALTHCHECK_PORT=8000

# ============================================
# ВНЕШНИЕ ИНТЕГРАЦИИ
# ============================================

# S3 для хранения файлов (опционально)
S3_ENABLED=false
S3_BUCKET=geobot-output
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_ENDPOINT=https://s3.amazonaws.com
S3_REGION=us-east-1

# Webhook URL для уведомлений
WEBHOOK_URL=

# Email уведомления (опционально)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=noreply@your-domain.com

# ============================================
# ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ
# ============================================

# Таймзона
TZ=Europe/Moscow

# Включить отладочный режим
DEBUG=false

# Включить профилирование производительности
ENABLE_PROFILING=false

# Лимит оперативной памяти на проект (MB)
MEMORY_LIMIT_PER_PROJECT=1024
```

### Безопасное хранение секретов

#### Использование Docker Secrets

```bash
# Создание secret
echo "my_bot_token" | docker secret create bot_token -

# Использование в docker-compose.yml
services:
  bot:
    secrets:
      - bot_token
    environment:
      BOT_TOKEN_FILE: /run/secrets/bot_token

secrets:
  bot_token:
    external: true
```

#### Использование HashiCorp Vault

```python
# src/config.py

import hvac

class VaultConfig:
    """Конфигурация из HashiCorp Vault"""
    
    def __init__(self):
        self.client = hvac.Client(url='http://vault:8200')
        self.client.token = os.getenv('VAULT_TOKEN')
    
    def get_secret(self, path: str) -> dict:
        """Получение секрета из Vault"""
        secret = self.client.secrets.kv.v2.read_secret_version(path=path)
        return secret['data']['data']

# Использование
vault = VaultConfig()
bot_config = vault.get_secret('geobot/bot')
BOT_TOKEN = bot_config['token']
```

## Логирование

### Конфигурация логирования

```python
# src/utils/logger.py

import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger
import os

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Кастомный JSON форматтер для логов"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['service'] = 'dxf-geobot'
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')
        log_record['level'] = record.levelname

def setup_logger(name: str = 'geobot') -> logging.Logger:
    """Настройка логгера"""
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
    
    # Избегаем дублирования handlers
    if logger.handlers:
        return logger
    
    # Формат логов
    log_format = os.getenv('LOG_FORMAT', 'json')
    
    if log_format == 'json':
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    if os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true':
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler с ротацией
    if os.getenv('LOG_TO_FILE', 'true').lower() == 'true':
        log_dir = os.getenv('LOGS_DIR', './logs')
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, 'bot.log'),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Отдельный файл для ошибок
        error_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, 'errors.log'),
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger

# Глобальный логгер
logger = setup_logger()
```

### Структурированное логирование

```python
# Использование в коде

from src.utils.logger import logger

# Информационное сообщение
logger.info("Processing started", extra={
    'user_id': user_id,
    'project_id': project_id,
    'points_count': len(points)
})

# Предупреждение
logger.warning("High memory usage", extra={
    'memory_mb': memory_usage,
    'threshold_mb': memory_threshold
})

# Ошибка с трейсбеком
try:
    process_data(data)
except Exception as e:
    logger.error("Processing failed", extra={
        'error': str(e),
        'data_size': len(data)
    }, exc_info=True)
```

### Централизованное логирование (ELK Stack)

```yaml
# docker-compose.yml - добавить сервисы ELK

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - geobot-network

  logstash:
    image: docker.elastic.co/logstash/logstash:8.10.0
    volumes:
      - ./logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf:ro
    networks:
      - geobot-network
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    networks:
      - geobot-network
    depends_on:
      - elasticsearch
```

```conf
# logstash/logstash.conf

input {
  file {
    path => "/app/logs/bot.log"
    codec => "json"
  }
}

filter {
  if [level] == "ERROR" {
    mutate {
      add_tag => ["error"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "geobot-logs-%{+YYYY.MM.dd}"
  }
}
```

## Мониторинг

### Prometheus метрики

```python
# src/utils/metrics.py

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Метрики
requests_total = Counter(
    'geobot_requests_total',
    'Total number of requests',
    ['method', 'status']
)

processing_duration = Histogram(
    'geobot_processing_duration_seconds',
    'Processing duration in seconds',
    ['operation']
)

active_projects = Gauge(
    'geobot_active_projects',
    'Number of active projects'
)

points_processed = Counter(
    'geobot_points_processed_total',
    'Total number of points processed'
)

errors_total = Counter(
    'geobot_errors_total',
    'Total number of errors',
    ['error_type']
)

# Запуск HTTP сервера для метрик
def start_metrics_server(port: int = 8000):
    """Запуск сервера метрик"""
    start_http_server(port)

# Использование в коде
class MetricsMiddleware:
    """Middleware для сбора метрик"""
    
    @staticmethod
    def track_request(method: str, status: str):
        requests_total.labels(method=method, status=status).inc()
    
    @staticmethod
    def track_processing(operation: str):
        """Декоратор для отслеживания времени обработки"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                with processing_duration.labels(operation=operation).time():
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def track_error(error_type: str):
        errors_total.labels(error_type=error_type).inc()
```

### Grafana дашборды

```yaml
# monitoring/grafana/dashboards/geobot.json

{
  "dashboard": {
    "title": "GeoBot Monitoring",
    "panels": [
      {
        "title": "Requests Rate",
        "targets": [
          {
            "expr": "rate(geobot_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Processing Duration",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, geobot_processing_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Active Projects",
        "targets": [
          {
            "expr": "geobot_active_projects"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(geobot_errors_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Alerts (Alertmanager)

```yaml
# monitoring/prometheus/alerts.yml

groups:
  - name: geobot_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(geobot_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"
      
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes{container="dxf-geobot"} / container_spec_memory_limit_bytes > 0.9
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage"
          description: "Memory usage is at {{ $value }}%"
      
      - alert: BotDown
        expr: up{job="geobot"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Bot is down"
          description: "GeoBot has been down for more than 1 minute"
```

## Резервное копирование

### Скрипт автоматического бэкапа

```bash
#!/bin/bash
# scripts/backup.sh

set -e

# Конфигурация
BACKUP_DIR="/backup/geobot"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

# Создание директории для бэкапов
mkdir -p "$BACKUP_DIR"

echo "Starting backup at $DATE"

# Бэкап базы данных
echo "Backing up database..."
docker-compose exec -T postgres pg_dump -U geobot geobot | \
  gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Бэкап файлов конфигурации
echo "Backing up configuration..."
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
  .env templates/ nginx/

# Бэкап выходных файлов (опционально)
echo "Backing up output files..."
tar -czf "$BACKUP_DIR/output_$DATE.tar.gz" output/

# Загрузка в S3 (опционально)
if [ "$UPLOAD_TO_S3" = "true" ]; then
  echo "Uploading to S3..."
  aws s3 cp "$BACKUP_DIR/db_$DATE.sql.gz" \
    s3://your-bucket/backups/db/
  aws s3 cp "$BACKUP_DIR/config_$DATE.tar.gz" \
    s3://your-bucket/backups/config/
fi

# Удаление старых бэкапов
echo "Cleaning old backups..."
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed successfully"
```

### Автоматизация через cron

```bash
# Редактирование crontab
crontab -e

# Добавить строку для ежедневного бэкапа в 2:00
0 2 * * * /home/geobot/dxf-geobot/scripts/backup.sh >> /var/log/geobot-backup.log 2>&1
```

## Масштабирование

### Горизонтальное масштабирование

```yaml
# docker-compose.scale.yml

services:
  bot:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  nginx:
    # Настройка балансировки нагрузки
    depends_on:
      - bot
```

### Kubernetes развертывание

```yaml
# k8s/deployment.yml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: geobot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: geobot
  template:
    metadata:
      labels:
        app: geobot
    spec:
      containers:
      - name: geobot
        image: your-registry/geobot:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        env:
        - name: BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: geobot-secrets
              key: bot-token
        volumeMounts:
        - name: templates
          mountPath: /app/templates
        - name: output
          mountPath: /app/output
      volumes:
      - name: templates
        persistentVolumeClaim:
          claimName: templates-pvc
      - name: output
        persistentVolumeClaim:
          claimName: output-pvc
```

## Безопасность

### Checklist безопасности

- [ ] Использовать HTTPS для всех подключений
- [ ] Хранить секреты в защищенном хранилище (Vault, Docker Secrets)
- [ ] Ограничить доступ к боту списком разрешенных пользователей
- [ ] Настроить firewall (UFW)
- [ ] Включить fail2ban для защиты от брутфорса
- [ ] Регулярно обновлять зависимости
- [ ] Использовать не-root пользователя в Docker
- [ ] Ограничить ресурсы контейнеров
- [ ] Включить логирование всех операций
- [ ] Настроить мониторинг безопасности
- [ ] Регулярно делать бэкапы
- [ ] Использовать сканирование уязвимостей (Trivy, Snyk)

### Сканирование образов Docker

```bash
# Установка Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -

# Сканирование образа
trivy image dxf-geobot:latest

# Сканирование с высоким приоритетом
trivy image --severity HIGH,CRITICAL dxf-geobot:latest
```

---

[← Руководство разработчика](./developer-guide.md) | [Монетизация →](./monetization.md)
