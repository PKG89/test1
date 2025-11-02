# Установка и настройка

Данное руководство содержит детальные инструкции по установке и настройке DXF Геообработка Бота.

## Содержание

- [Системные требования](#системные-требования)
- [Установка Python и зависимостей](#установка-python-и-зависимостей)
- [Установка GDAL](#установка-gdal)
- [Настройка переменных окружения](#настройка-переменных-окружения)
- [Конфигурация бота](#конфигурация-бота)
- [Проверка установки](#проверка-установки)

## Системные требования

### Минимальные требования

- **ОС**: Linux (Ubuntu 20.04+), macOS 10.14+, Windows 10+
- **Python**: 3.8 или выше
- **RAM**: 2 GB (рекомендуется 4 GB+)
- **Дисковое пространство**: 500 MB для программы + место для данных
- **Процессор**: 2 ядра (рекомендуется 4+)

### Рекомендуемые требования для продакшена

- **ОС**: Ubuntu 22.04 LTS
- **Python**: 3.10+
- **RAM**: 8 GB+
- **Дисковое пространство**: 10 GB+
- **Процессор**: 4+ ядра

## Установка Python и зависимостей

### Ubuntu/Debian

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и необходимых пакетов
sudo apt install -y python3.10 python3.10-venv python3-pip

# Установка системных зависимостей
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

# Создание виртуального окружения
python3.10 -m venv venv
source venv/bin/activate

# Обновление pip
pip install --upgrade pip setuptools wheel
```

### macOS

```bash
# Установка Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установка Python
brew install python@3.10

# Создание виртуального окружения
python3.10 -m venv venv
source venv/bin/activate

# Обновление pip
pip install --upgrade pip setuptools wheel
```

### Windows

```powershell
# Скачать и установить Python 3.10+ с python.org
# Убедиться, что установлена опция "Add Python to PATH"

# Открыть PowerShell или CMD
python -m venv venv
.\venv\Scripts\activate

# Обновление pip
python -m pip install --upgrade pip setuptools wheel
```

## Установка GDAL

GDAL - критически важная библиотека для обработки геопространственных данных.

### Ubuntu/Debian

```bash
# Установка GDAL системной библиотеки
sudo apt install -y gdal-bin libgdal-dev

# Определение версии GDAL
gdal-config --version

# Установка Python-биндингов (замените версию на вашу)
pip install GDAL==$(gdal-config --version)
```

### macOS

```bash
# Установка GDAL через Homebrew
brew install gdal

# Установка Python-биндингов
pip install GDAL==$(gdal-config --version)
```

### Windows

```powershell
# Скачать предсобранные wheels с
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal

# Установить скачанный wheel
pip install GDAL-3.x.x-cpxx-cpxxm-win_amd64.whl
```

## Установка основных зависимостей

После установки GDAL установите остальные зависимости:

```bash
# Активация виртуального окружения (если еще не активировано)
source venv/bin/activate  # Linux/macOS
# или
.\venv\Scripts\activate   # Windows

# Установка зависимостей из requirements.txt
pip install -r requirements.txt
```

### Содержание requirements.txt

```txt
numpy>=1.21.0
scipy>=1.7.0
shapely>=1.8.0
Pillow>=9.0.0
requests>=2.27.0
python-telegram-bot>=13.11
python-dotenv>=0.19.0
ezdxf>=0.17.0
matplotlib>=3.5.0
pandas>=1.3.0
```

### Установка без requirements.txt

```bash
pip install numpy scipy shapely Pillow requests python-telegram-bot python-dotenv ezdxf matplotlib pandas
```

## Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта:

```bash
# Копирование шаблона
cp .env.example .env

# Редактирование файла
nano .env  # или используйте ваш любимый редактор
```

### Пример .env файла

```env
# Настройки бота
BOT_TOKEN=your_telegram_bot_token_here
BOT_USERNAME=your_bot_username

# Настройки обработки
MAX_POINTS=1000000
DEFAULT_SCALE=1000
TIN_METHOD=delaunay
DENSIFY_FACTOR=2.0

# Пути к файлам
TEMPLATES_DIR=./templates
OUTPUT_DIR=./output
TEMP_DIR=./temp
LOGS_DIR=./logs

# База данных (опционально)
DATABASE_URL=sqlite:///./data.db

# Настройки безопасности
ALLOWED_USERS=
MAX_FILE_SIZE=50  # MB

# Настройки логирования
LOG_LEVEL=INFO
LOG_FORMAT=json

# Рабочие настройки
WORKERS=4
TIMEOUT=300  # секунды

# Интеграции (опционально)
SENTRY_DSN=
REDIS_URL=redis://localhost:6379/0
```

### Получение Telegram Bot Token

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте токен и вставьте в `.env` файл
5. (Опционально) Настройте команды бота через `/setcommands`

## Конфигурация бота

### Создание необходимых директорий

```bash
mkdir -p templates output temp logs data
```

### Настройка прав доступа (Linux/macOS)

```bash
chmod 755 templates output temp logs
chmod 600 .env  # Защита конфиденциальных данных
```

### Структура проекта

После установки структура должна выглядеть так:

```
project/
├── bot.py                  # Основной файл бота
├── requirements.txt        # Зависимости Python
├── .env                    # Переменные окружения (не комитится!)
├── .env.example           # Пример конфигурации
├── .gitignore             # Git ignore файл
├── Dockerfile             # Docker конфигурация
├── docker-compose.yml     # Docker Compose файл
├── README.md              # Основная документация
├── docs/                  # Документация
│   ├── installation.md
│   ├── user-guide.md
│   ├── developer-guide.md
│   ├── deployment.md
│   └── monetization.md
├── src/                   # Исходный код
│   ├── __init__.py
│   ├── processors/        # Процессоры данных
│   ├── templates/         # Работа с шаблонами
│   ├── utils/            # Утилиты
│   └── handlers/         # Обработчики бота
├── templates/            # DXF шаблоны
├── output/              # Выходные файлы
├── temp/                # Временные файлы
├── logs/                # Логи
└── tests/               # Тесты
```

## Проверка установки

### Проверка Python пакетов

```bash
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import scipy; print('SciPy:', scipy.__version__)"
python -c "import shapely; print('Shapely:', shapely.__version__)"
python -c "from osgeo import gdal; print('GDAL:', gdal.__version__)"
python -c "import PIL; print('Pillow:', PIL.__version__)"
python -c "import requests; print('Requests:', requests.__version__)"
```

### Тестовый запуск

```bash
# Проверка конфигурации
python -m src.utils.check_config

# Запуск тестов (если доступны)
python -m pytest tests/

# Запуск бота в режиме отладки
python bot.py --debug
```

### Ожидаемый вывод

```
✓ Configuration loaded successfully
✓ All dependencies installed
✓ GDAL version: 3.4.1
✓ Bot token configured
✓ Directories created
✓ Ready to start
```

## Устранение распространенных проблем

### Проблема: GDAL не устанавливается

**Решение для Ubuntu:**
```bash
sudo add-apt-repository ppa:ubuntugis/ppa
sudo apt update
sudo apt install gdal-bin libgdal-dev
```

**Решение для macOS:**
```bash
brew reinstall gdal
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install GDAL==$(gdal-config --version)
```

### Проблема: NumPy/SciPy ошибки компиляции

```bash
# Установка OpenBLAS (Ubuntu)
sudo apt install libopenblas-dev

# Или использование conda
conda install numpy scipy
```

### Проблема: Ошибки прав доступа

```bash
# Проверка владельца директорий
ls -la

# Исправление прав
sudo chown -R $USER:$USER .
chmod -R 755 .
```

### Проблема: Бот не запускается

1. Проверьте токен бота в `.env`
2. Убедитесь, что все зависимости установлены
3. Проверьте логи: `tail -f logs/bot.log`
4. Проверьте доступность Telegram API: `ping api.telegram.org`

## Обновление

### Обновление зависимостей

```bash
# Активация окружения
source venv/bin/activate

# Обновление всех пакетов
pip install --upgrade -r requirements.txt

# Или обновление конкретного пакета
pip install --upgrade numpy
```

### Обновление из Git

```bash
# Сохранение локальных изменений
git stash

# Получение обновлений
git pull origin main

# Применение изменений
git stash pop

# Обновление зависимостей
pip install -r requirements.txt

# Миграция данных (если требуется)
python -m src.utils.migrate
```

## Следующие шаги

После успешной установки переходите к:

- **[Руководству пользователя](./user-guide.md)** - для начала работы с ботом
- **[Руководству разработчика](./developer-guide.md)** - для разработки и расширения
- **[Развертыванию](./deployment.md)** - для продакшен деплоя

## Поддержка

Если у вас возникли проблемы с установкой:

1. Проверьте [Issues на GitHub](https://github.com/your-repo/issues)
2. Создайте новый Issue с описанием проблемы
3. Свяжитесь с поддержкой: support@example.com

---

[← Назад к README](../README.md) | [Руководство пользователя →](./user-guide.md)
