# Монетизация

Руководство по стратегиям монетизации DXF Геообработка Бота, включая модели подписок, платного доступа и десктопных приложений.

## Содержание

- [Обзор моделей монетизации](#обзор-моделей-монетизации)
- [SaaS подписка](#saas-подписка)
- [Платный доступ к боту](#платный-доступ-к-боту)
- [Десктопное приложение](#десктопное-приложение)
- [Корпоративные решения](#корпоративные-решения)
- [Дополнительные источники дохода](#дополнительные-источники-дохода)
- [Ценообразование](#ценообразование)
- [Техническая реализация платежей](#техническая-реализация-платежей)

## Обзор моделей монетизации

### Сравнение моделей

| Модель | Сложность внедрения | Потенциальный доход | Целевая аудитория |
|--------|---------------------|---------------------|-------------------|
| Freemium бот | ⭐ Низкая | 💰 Средний | Индивидуальные пользователи |
| SaaS подписка | ⭐⭐ Средняя | 💰💰 Высокий | Компании, профессионалы |
| Платный бот-доступ | ⭐ Низкая | 💰 Средний | Профессионалы |
| Десктопное приложение | ⭐⭐⭐ Высокая | 💰💰💰 Очень высокий | Корпоративные клиенты |
| Enterprise решение | ⭐⭐⭐ Высокая | 💰💰💰💰 Максимальный | Крупные компании |
| API-доступ | ⭐⭐ Средняя | 💰💰 Высокий | Разработчики, интеграторы |

### Рекомендуемая стратегия

**Этап 1 (месяцы 0-3):** Freemium модель для набора пользовательской базы
**Этап 2 (месяцы 3-6):** Запуск платных подписок с расширенными функциями
**Этап 3 (месяцы 6-12):** Добавление корпоративных тарифов и API
**Этап 4 (месяцы 12+):** Разработка десктопного приложения для премиум сегмента

## SaaS подписка

### Модель подписки

#### Freemium тарифный план

**Бесплатный (Free)**
- ✅ До 1,000 точек на проект
- ✅ 5 проектов в месяц
- ✅ Базовые шаблоны (3 шт.)
- ✅ Экспорт в DXF (R2013)
- ✅ Email поддержка (48ч)
- ❌ Водяной знак на чертежах

**Стартовый (Starter)** - 990₽/мес ($12/мес)
- ✅ До 10,000 точек на проект
- ✅ 30 проектов в месяц
- ✅ Расширенные шаблоны (10 шт.)
- ✅ Экспорт в DXF (R2018) и PDF
- ✅ Построение TIN
- ✅ Денсификация (до 2x)
- ✅ Email поддержка (24ч)
- ✅ Без водяных знаков

**Профессиональный (Professional)** - 2,990₽/мес ($35/мес)
- ✅ До 100,000 точек на проект
- ✅ Неограниченное количество проектов
- ✅ Все шаблоны + загрузка своих
- ✅ Экспорт в DXF, PDF, PNG, SVG
- ✅ Построение TIN с настройками
- ✅ Денсификация (до 5x)
- ✅ Работа с LAS/LAZ файлами
- ✅ Пакетная обработка
- ✅ Приоритетная поддержка (12ч)
- ✅ API доступ (1000 запросов/день)

**Бизнес (Business)** - 9,990₽/мес ($120/мес)
- ✅ Неограниченное количество точек
- ✅ Неограниченное количество проектов
- ✅ Все возможности Professional
- ✅ Белый лейбл (свой брендинг)
- ✅ Приоритетная обработка
- ✅ API доступ (неограниченный)
- ✅ Интеграция с корпоративными системами
- ✅ Выделенная поддержка 24/7
- ✅ SLA гарантии
- ✅ Обучение команды

**Enterprise** - от 29,990₽/мес (индивидуально)
- ✅ Все возможности Business
- ✅ On-premise развертывание
- ✅ Кастомизация под требования
- ✅ Интеграция с ГИС системами
- ✅ Персональный менеджер
- ✅ Разработка специфичных функций
- ✅ Консультации специалистов

### Техническая реализация подписок

#### Модель данных

```python
# src/models/subscription.py

from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

class SubscriptionTier(Enum):
    """Уровни подписки"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

@dataclass
class SubscriptionLimits:
    """Лимиты подписки"""
    max_points_per_project: int
    max_projects_per_month: int
    max_file_size_mb: int
    has_api_access: bool
    api_requests_per_day: Optional[int]
    has_batch_processing: bool
    has_las_support: bool
    support_response_time_hours: int
    watermark: bool

class Subscription:
    """Модель подписки"""
    
    TIER_LIMITS = {
        SubscriptionTier.FREE: SubscriptionLimits(
            max_points_per_project=1_000,
            max_projects_per_month=5,
            max_file_size_mb=5,
            has_api_access=False,
            api_requests_per_day=None,
            has_batch_processing=False,
            has_las_support=False,
            support_response_time_hours=48,
            watermark=True
        ),
        SubscriptionTier.STARTER: SubscriptionLimits(
            max_points_per_project=10_000,
            max_projects_per_month=30,
            max_file_size_mb=20,
            has_api_access=False,
            api_requests_per_day=None,
            has_batch_processing=False,
            has_las_support=False,
            support_response_time_hours=24,
            watermark=False
        ),
        SubscriptionTier.PROFESSIONAL: SubscriptionLimits(
            max_points_per_project=100_000,
            max_projects_per_month=-1,  # Unlimited
            max_file_size_mb=100,
            has_api_access=True,
            api_requests_per_day=1_000,
            has_batch_processing=True,
            has_las_support=True,
            support_response_time_hours=12,
            watermark=False
        ),
        SubscriptionTier.BUSINESS: SubscriptionLimits(
            max_points_per_project=-1,  # Unlimited
            max_projects_per_month=-1,
            max_file_size_mb=500,
            has_api_access=True,
            api_requests_per_day=-1,  # Unlimited
            has_batch_processing=True,
            has_las_support=True,
            support_response_time_hours=1,
            watermark=False
        ),
    }
    
    def __init__(self, user_id: int, tier: SubscriptionTier,
                 expires_at: datetime):
        self.user_id = user_id
        self.tier = tier
        self.expires_at = expires_at
        self.created_at = datetime.now()
    
    @property
    def is_active(self) -> bool:
        """Проверка активности подписки"""
        return datetime.now() < self.expires_at
    
    @property
    def limits(self) -> SubscriptionLimits:
        """Получение лимитов подписки"""
        return self.TIER_LIMITS[self.tier]
    
    def can_process_points(self, points_count: int) -> bool:
        """Проверка возможности обработки количества точек"""
        max_points = self.limits.max_points_per_project
        return max_points == -1 or points_count <= max_points
```

#### Проверка лимитов

```python
# src/services/subscription_service.py

from src.models.subscription import Subscription, SubscriptionTier
from src.database.models import User, Project
from datetime import datetime

class SubscriptionService:
    """Сервис управления подписками"""
    
    async def get_user_subscription(self, user_id: int) -> Subscription:
        """Получение подписки пользователя"""
        # Загрузка из БД
        user = await User.get(user_id)
        
        if user.subscription_tier and user.subscription_expires_at:
            return Subscription(
                user_id=user_id,
                tier=SubscriptionTier(user.subscription_tier),
                expires_at=user.subscription_expires_at
            )
        
        # Бесплатная подписка по умолчанию
        return Subscription(
            user_id=user_id,
            tier=SubscriptionTier.FREE,
            expires_at=datetime.max
        )
    
    async def check_project_limit(self, user_id: int) -> bool:
        """Проверка лимита проектов за месяц"""
        subscription = await self.get_user_subscription(user_id)
        
        if subscription.limits.max_projects_per_month == -1:
            return True
        
        # Подсчет проектов за текущий месяц
        current_month_projects = await Project.count_by_user_this_month(user_id)
        
        return current_month_projects < subscription.limits.max_projects_per_month
    
    async def upgrade_subscription(self, user_id: int, 
                                   new_tier: SubscriptionTier,
                                   payment_id: str) -> Subscription:
        """Повышение уровня подписки"""
        user = await User.get(user_id)
        
        # Расчет даты окончания
        if new_tier == SubscriptionTier.FREE:
            expires_at = datetime.max
        else:
            expires_at = datetime.now() + timedelta(days=30)
        
        # Обновление в БД
        user.subscription_tier = new_tier.value
        user.subscription_expires_at = expires_at
        user.last_payment_id = payment_id
        await user.save()
        
        return Subscription(user_id, new_tier, expires_at)
```

#### Интеграция в бот

```python
# src/bot/handlers.py

from src.services.subscription_service import SubscriptionService

async def new_project_handler(update: Update, context: CallbackContext):
    """Обработчик создания проекта с проверкой лимитов"""
    user_id = update.effective_user.id
    
    subscription_service = SubscriptionService()
    
    # Проверка лимита проектов
    can_create = await subscription_service.check_project_limit(user_id)
    
    if not can_create:
        subscription = await subscription_service.get_user_subscription(user_id)
        await update.message.reply_text(
            f"❌ Достигнут лимит проектов для тарифа {subscription.tier.value}\n"
            f"Лимит: {subscription.limits.max_projects_per_month} проектов/месяц\n\n"
            f"Повысьте тариф для увеличения лимитов: /upgrade"
        )
        return
    
    # Продолжить создание проекта
    context.user_data['state'] = 'AWAITING_FILE'
    await update.message.reply_text("Отправьте файл с координатами")

async def upgrade_command(update: Update, context: CallbackContext):
    """Команда повышения тарифа"""
    user_id = update.effective_user.id
    subscription_service = SubscriptionService()
    subscription = await subscription_service.get_user_subscription(user_id)
    
    keyboard = [
        [InlineKeyboardButton("Starter - 990₽/мес", callback_data="upgrade_starter")],
        [InlineKeyboardButton("Professional - 2,990₽/мес", callback_data="upgrade_professional")],
        [InlineKeyboardButton("Business - 9,990₽/мес", callback_data="upgrade_business")],
        [InlineKeyboardButton("Enterprise - связаться", url="https://t.me/support")]
    ]
    
    await update.message.reply_text(
        f"Ваш текущий тариф: {subscription.tier.value}\n\n"
        f"Выберите новый тариф:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
```

## Платный доступ к боту

### Модель оплаты за использование (Pay-as-you-go)

**Преимущества:**
- Низкий порог входа для пользователей
- Оплата только за реальное использование
- Гибкое ценообразование

**Ценообразование:**
- 10₽ за 1,000 точек обработки
- 50₽ за построение TIN
- 30₽ за денсификацию
- 100₽ за обработку LAS файла

#### Реализация кредитной системы

```python
# src/models/credits.py

from dataclasses import dataclass
from datetime import datetime

@dataclass
class CreditPack:
    """Пакет кредитов"""
    name: str
    credits: int
    price_rub: int
    bonus_credits: int = 0
    
    @property
    def total_credits(self) -> int:
        return self.credits + self.bonus_credits

# Доступные пакеты
CREDIT_PACKS = [
    CreditPack("Начальный", credits=100, price_rub=500, bonus_credits=0),
    CreditPack("Стандартный", credits=500, price_rub=2000, bonus_credits=50),
    CreditPack("Премиум", credits=1500, price_rub=5000, bonus_credits=300),
    CreditPack("Профессиональный", credits=5000, price_rub=15000, bonus_credits=1500),
]

class CreditAccount:
    """Аккаунт с кредитами"""
    
    OPERATION_COSTS = {
        'process_1000_points': 10,
        'build_tin': 50,
        'densify': 30,
        'process_las': 100,
        'export_pdf': 20,
        'api_request': 1,
    }
    
    def __init__(self, user_id: int, balance: int = 0):
        self.user_id = user_id
        self.balance = balance
    
    def has_credits(self, operation: str) -> bool:
        """Проверка наличия кредитов для операции"""
        cost = self.OPERATION_COSTS.get(operation, 0)
        return self.balance >= cost
    
    def charge(self, operation: str, multiplier: float = 1.0) -> bool:
        """Списание кредитов за операцию"""
        cost = int(self.OPERATION_COSTS.get(operation, 0) * multiplier)
        
        if self.balance >= cost:
            self.balance -= cost
            return True
        return False
    
    def add_credits(self, amount: int):
        """Добавление кредитов"""
        self.balance += amount
```

## Десктопное приложение

### Концепция десктопного решения

**Целевая аудитория:**
- Геодезические компании
- Проектные организации
- Крупные строительные компании

**Преимущества десктопного приложения:**
- ✅ Работа без интернета
- ✅ Обработка очень больших файлов (миллионы точек)
- ✅ Интеграция с локальными CAD системами
- ✅ Повышенная безопасность данных
- ✅ Расширенные возможности настройки

### Стек технологий

```
Desktop Application Stack:
├── Frontend: Electron + React
├── Backend: Python (встроенный)
├── Processing: NumPy, SciPy (оптимизированные)
└── CAD Engine: ezdxf, pythonOCC
```

### Модель распространения

**Вариант 1: Perpetual License (бессрочная лицензия)**
- Единоразовая оплата: 49,990₽
- Включает 1 год обновлений и поддержки
- Продление поддержки: 9,990₽/год

**Вариант 2: Subscription License (подписка)**
- Годовая подписка: 19,990₽/год
- Включает все обновления и поддержку
- Скидка при оплате за 3 года: 49,990₽

**Вариант 3: Network License (сетевая лицензия)**
- От 5 одновременных пользователей
- Цена: от 149,990₽ + 29,990₽/год поддержка
- Центральное управление лицензиями

### Структура проекта

```
desktop-app/
├── electron/              # Electron оболочка
│   ├── main.js           # Главный процесс
│   ├── preload.js        # Preload скрипт
│   └── package.json
│
├── frontend/             # React интерфейс
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
│
├── backend/              # Python backend
│   ├── api/             # REST API для фронтенда
│   ├── processors/      # Обработка данных
│   └── requirements.txt
│
├── build/               # Сборка приложения
│   ├── windows/
│   ├── macos/
│   └── linux/
│
└── installer/           # Установщики
    ├── windows.nsis
    ├── macos.dmg
    └── linux.AppImage
```

### Система лицензирования

```python
# backend/licensing.py

import hashlib
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import uuid

class LicenseManager:
    """Менеджер лицензий"""
    
    def __init__(self, secret_key: bytes):
        self.cipher = Fernet(secret_key)
    
    def generate_license(self, user_info: dict, license_type: str,
                        duration_days: int = 365) -> str:
        """Генерация лицензионного ключа"""
        license_data = {
            'user_id': user_info['user_id'],
            'email': user_info['email'],
            'company': user_info.get('company', ''),
            'type': license_type,  # perpetual, subscription, network
            'issued_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=duration_days)).isoformat(),
            'machine_id': user_info.get('machine_id', ''),
            'features': self._get_features_for_type(license_type),
        }
        
        # Шифрование лицензии
        license_json = json.dumps(license_data)
        encrypted = self.cipher.encrypt(license_json.encode())
        
        # Генерация читаемого ключа
        license_key = self._format_license_key(encrypted)
        
        return license_key
    
    def validate_license(self, license_key: str, machine_id: str) -> dict:
        """Валидация лицензии"""
        try:
            # Расшифровка
            encrypted = self._parse_license_key(license_key)
            decrypted = self.cipher.decrypt(encrypted)
            license_data = json.loads(decrypted.decode())
            
            # Проверка срока действия
            expires_at = datetime.fromisoformat(license_data['expires_at'])
            if datetime.now() > expires_at and license_data['type'] != 'perpetual':
                return {'valid': False, 'reason': 'expired'}
            
            # Проверка привязки к машине (если указана)
            if license_data.get('machine_id') and \
               license_data['machine_id'] != machine_id:
                return {'valid': False, 'reason': 'machine_mismatch'}
            
            return {'valid': True, 'license_data': license_data}
        
        except Exception as e:
            return {'valid': False, 'reason': str(e)}
    
    def _get_features_for_type(self, license_type: str) -> list:
        """Получение функций для типа лицензии"""
        features_map = {
            'perpetual': ['all_features', 'offline', 'unlimited_projects'],
            'subscription': ['all_features', 'offline', 'unlimited_projects', 'updates'],
            'network': ['all_features', 'offline', 'unlimited_projects', 
                       'updates', 'central_management'],
        }
        return features_map.get(license_type, [])
    
    def _format_license_key(self, encrypted: bytes) -> str:
        """Форматирование ключа в читаемый вид"""
        # Конвертация в hex и разделение на группы
        hex_key = encrypted.hex().upper()
        groups = [hex_key[i:i+4] for i in range(0, len(hex_key), 4)]
        return '-'.join(groups[:8])  # Первые 8 групп для компактности
    
    def _parse_license_key(self, license_key: str) -> bytes:
        """Парсинг ключа обратно в bytes"""
        hex_key = license_key.replace('-', '')
        return bytes.fromhex(hex_key)

# Использование
license_manager = LicenseManager(secret_key=b'your-secret-key-here')

# Генерация лицензии
user_info = {
    'user_id': 12345,
    'email': 'user@company.com',
    'company': 'GeoTech LLC',
    'machine_id': uuid.getnode()  # MAC адрес
}
license_key = license_manager.generate_license(
    user_info, 
    license_type='subscription',
    duration_days=365
)

# Валидация
result = license_manager.validate_license(license_key, str(uuid.getnode()))
if result['valid']:
    print("Лицензия действительна")
else:
    print(f"Ошибка лицензии: {result['reason']}")
```

## Корпоративные решения

### Enterprise Package

**Что включено:**
- ✅ On-premise развертывание
- ✅ Интеграция с корпоративной инфраструктурой (AD, SSO)
- ✅ Кастомизация под бизнес-процессы
- ✅ Интеграция с существующими ГИС системами
- ✅ Обучение персонала
- ✅ Выделенная поддержка 24/7
- ✅ SLA гарантии 99.9%
- ✅ Персональный менеджер

**Ценообразование:**
- Базовая стоимость: 499,990₽
- Настройка и интеграция: от 199,990₽
- Годовая поддержка: 149,990₽
- Обучение (3 дня): 99,990₽

### Интеграция с корпоративными системами

```python
# src/integrations/corporate.py

from typing import Protocol
import ldap
import requests

class SSOProvider(Protocol):
    """Протокол SSO провайдера"""
    def authenticate(self, token: str) -> dict: ...

class ActiveDirectorySSO:
    """Интеграция с Active Directory"""
    
    def __init__(self, server: str, base_dn: str):
        self.server = server
        self.base_dn = base_dn
    
    def authenticate(self, username: str, password: str) -> dict:
        """Аутентификация через AD"""
        try:
            conn = ldap.initialize(f'ldap://{self.server}')
            user_dn = f'cn={username},{self.base_dn}'
            conn.simple_bind_s(user_dn, password)
            
            # Получение атрибутов пользователя
            result = conn.search_s(
                user_dn, 
                ldap.SCOPE_BASE,
                attrlist=['mail', 'displayName', 'department']
            )
            
            user_data = result[0][1]
            
            return {
                'authenticated': True,
                'email': user_data.get('mail', [b''])[0].decode(),
                'name': user_data.get('displayName', [b''])[0].decode(),
                'department': user_data.get('department', [b''])[0].decode(),
            }
        
        except ldap.INVALID_CREDENTIALS:
            return {'authenticated': False, 'error': 'Invalid credentials'}
        except Exception as e:
            return {'authenticated': False, 'error': str(e)}

class GISIntegration:
    """Интеграция с ГИС системами"""
    
    def __init__(self, gis_api_url: str, api_key: str):
        self.api_url = gis_api_url
        self.api_key = api_key
    
    def export_to_gis(self, project_id: str, layer_name: str) -> bool:
        """Экспорт проекта в ГИС систему"""
        # Получение данных проекта
        project_data = self._get_project_data(project_id)
        
        # Конвертация в GeoJSON
        geojson = self._convert_to_geojson(project_data)
        
        # Отправка в ГИС
        response = requests.post(
            f'{self.api_url}/layers/{layer_name}/features',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json=geojson
        )
        
        return response.status_code == 201
```

## Дополнительные источники дохода

### 1. API Marketplace

Предоставление API для сторонних разработчиков:

```python
# API ценообразование
API_PRICING = {
    'free': {
        'requests_per_month': 1_000,
        'rate_limit': '10/minute',
        'price': 0
    },
    'developer': {
        'requests_per_month': 10_000,
        'rate_limit': '100/minute',
        'price': 2_990  # руб/мес
    },
    'business': {
        'requests_per_month': 100_000,
        'rate_limit': '1000/minute',
        'price': 19_990
    },
    'enterprise': {
        'requests_per_month': -1,  # unlimited
        'rate_limit': '10000/minute',
        'price': 'custom'
    }
}
```

### 2. Платные шаблоны и расширения

**Магазин шаблонов:**
- Отраслевые шаблоны: 990₽
- Премиум шаблоны: 2,990₽
- Пакеты шаблонов: 9,990₽

**Расширения функциональности:**
- Модуль генерации отчетов: 4,990₽
- Модуль 3D визуализации: 7,990₽
- Модуль анализа рельефа: 5,990₽

### 3. Обучение и сертификация

**Онлайн курсы:**
- Базовый курс: 4,990₽
- Продвинутый курс: 9,990₽
- Профессиональная сертификация: 19,990₽

**Корпоративное обучение:**
- Вебинар (2 часа): 29,990₽
- Тренинг (1 день): 79,990₽
- Полный курс (3 дня): 199,990₽

### 4. Консультационные услуги

- Техническая консультация (1 час): 4,990₽
- Настройка интеграции: от 49,990₽
- Разработка custom решений: от 199,990₽

## Ценообразование

### Калькулятор цен

```python
# src/services/pricing_calculator.py

from dataclasses import dataclass
from typing import Dict

@dataclass
class PricingFactors:
    """Факторы ценообразования"""
    points_count: int
    has_tin: bool = False
    has_densification: bool = False
    densification_factor: float = 1.0
    export_formats: list = None
    processing_time_seconds: float = 0
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ['dxf']

class PricingCalculator:
    """Калькулятор стоимости обработки"""
    
    # Базовые цены (в рублях)
    PRICE_PER_1000_POINTS = 10
    PRICE_TIN = 50
    PRICE_DENSIFICATION_BASE = 30
    EXPORT_PRICES = {
        'dxf': 0,
        'pdf': 20,
        'png': 10,
        'svg': 15,
    }
    
    def calculate_cost(self, factors: PricingFactors) -> Dict:
        """Расчет стоимости"""
        cost_breakdown = {}
        
        # Стоимость обработки точек
        points_cost = (factors.points_count / 1000) * self.PRICE_PER_1000_POINTS
        cost_breakdown['points'] = points_cost
        
        # Стоимость TIN
        if factors.has_tin:
            cost_breakdown['tin'] = self.PRICE_TIN
        
        # Стоимость денсификации
        if factors.has_densification:
            densify_cost = self.PRICE_DENSIFICATION_BASE * factors.densification_factor
            cost_breakdown['densification'] = densify_cost
        
        # Стоимость экспорта
        export_cost = sum(
            self.EXPORT_PRICES.get(fmt, 0)
            for fmt in factors.export_formats
        )
        cost_breakdown['export'] = export_cost
        
        # Общая стоимость
        total = sum(cost_breakdown.values())
        
        return {
            'total': round(total, 2),
            'breakdown': cost_breakdown,
            'currency': 'RUB'
        }

# Использование
calculator = PricingCalculator()

factors = PricingFactors(
    points_count=15_000,
    has_tin=True,
    has_densification=True,
    densification_factor=2.0,
    export_formats=['dxf', 'pdf']
)

cost = calculator.calculate_cost(factors)
print(f"Стоимость обработки: {cost['total']} руб.")
print(f"Детализация: {cost['breakdown']}")
```

## Техническая реализация платежей

### Интеграция платежных систем

#### ЮKassa (Россия)

```python
# src/payments/yookassa.py

from yookassa import Configuration, Payment
import uuid

Configuration.account_id = 'your_shop_id'
Configuration.secret_key = 'your_secret_key'

class YooKassaPayment:
    """Обработка платежей через ЮKassa"""
    
    def create_payment(self, amount: float, description: str,
                      user_id: int, return_url: str) -> dict:
        """Создание платежа"""
        
        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,
            "metadata": {
                "user_id": user_id,
                "order_id": str(uuid.uuid4())
            }
        }, uuid.uuid4())
        
        return {
            'payment_id': payment.id,
            'confirmation_url': payment.confirmation.confirmation_url,
            'status': payment.status
        }
    
    def check_payment(self, payment_id: str) -> dict:
        """Проверка статуса платежа"""
        payment = Payment.find_one(payment_id)
        
        return {
            'payment_id': payment.id,
            'status': payment.status,
            'paid': payment.paid,
            'amount': float(payment.amount.value),
            'metadata': payment.metadata
        }
```

#### Telegram Payments

```python
# src/bot/payments.py

from telegram import LabeledPrice, Update
from telegram.ext import CallbackContext

async def send_invoice(update: Update, context: CallbackContext,
                      title: str, description: str,
                      price: int, currency: str = 'RUB'):
    """Отправка счета через Telegram Payments"""
    
    chat_id = update.effective_chat.id
    
    await context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload='subscription_payment',
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency=currency,
        prices=[LabeledPrice(title, price * 100)],  # в копейках
        start_parameter='subscription',
        photo_url='https://your-site.com/subscription-image.png',
        photo_size=512,
        photo_width=512,
        photo_height=512,
        need_email=True,
    )

async def precheckout_callback(update: Update, context: CallbackContext):
    """Обработка pre-checkout запроса"""
    query = update.pre_checkout_query
    
    # Валидация платежа
    if query.invoice_payload == 'subscription_payment':
        await query.answer(ok=True)
    else:
        await query.answer(
            ok=False,
            error_message="Что-то пошло не так..."
        )

async def successful_payment_callback(update: Update, context: CallbackContext):
    """Обработка успешного платежа"""
    payment = update.message.successful_payment
    user_id = update.effective_user.id
    
    # Активация подписки
    subscription_service = SubscriptionService()
    await subscription_service.upgrade_subscription(
        user_id,
        SubscriptionTier.STARTER,
        payment.provider_payment_charge_id
    )
    
    await update.message.reply_text(
        "✅ Платеж успешно обработан!\n"
        "Ваша подписка активирована."
    )
```

### Webhook для уведомлений о платежах

```python
# src/api/webhooks.py

from fastapi import FastAPI, Request
import hashlib
import hmac

app = FastAPI()

@app.post("/webhooks/yookassa")
async def yookassa_webhook(request: Request):
    """Webhook для уведомлений от ЮKassa"""
    
    # Получение данных
    body = await request.body()
    notification = await request.json()
    
    # Проверка подписи
    signature = request.headers.get('X-Signature')
    if not verify_signature(body, signature):
        return {"error": "Invalid signature"}, 403
    
    # Обработка уведомления
    event_type = notification.get('event')
    payment_data = notification.get('object')
    
    if event_type == 'payment.succeeded':
        await handle_successful_payment(payment_data)
    elif event_type == 'payment.canceled':
        await handle_canceled_payment(payment_data)
    
    return {"status": "ok"}

def verify_signature(body: bytes, signature: str) -> bool:
    """Проверка подписи webhook"""
    secret_key = 'your_webhook_secret'
    expected_signature = hmac.new(
        secret_key.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

async def handle_successful_payment(payment_data: dict):
    """Обработка успешного платежа"""
    user_id = payment_data['metadata']['user_id']
    amount = float(payment_data['amount']['value'])
    
    # Определение типа подписки по сумме
    tier_map = {
        990: SubscriptionTier.STARTER,
        2990: SubscriptionTier.PROFESSIONAL,
        9990: SubscriptionTier.BUSINESS,
    }
    
    tier = tier_map.get(int(amount))
    
    if tier:
        subscription_service = SubscriptionService()
        await subscription_service.upgrade_subscription(
            user_id, tier, payment_data['id']
        )
        
        # Отправка уведомления пользователю
        await send_notification(user_id, 
            f"✅ Подписка {tier.value} успешно активирована!"
        )
```

---

[← Развертывание](./deployment.md) | [README →](../README.md)
