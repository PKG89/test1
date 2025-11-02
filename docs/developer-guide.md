# Руководство разработчика

Подробное руководство по архитектуре кода, разработке и расширению функциональности DXF Геообработка Бота.

## Содержание

- [Архитектура проекта](#архитектура-проекта)
- [Модули и их ответственность](#модули-и-их-ответственность)
- [Сервисная архитектура](#сервисная-архитектура)
- [Добавление новых кодов и блоков](#добавление-новых-кодов-и-блоков)
- [Расширение функциональности](#расширение-функциональности)
- [Тестирование](#тестирование)
- [Стандарты кодирования](#стандарты-кодирования)

## Архитектура проекта

### Общая структура

Проект построен на модульной архитектуре с четким разделением ответственности:

```
project/
├── bot.py                      # Точка входа, инициализация бота
├── config.py                   # Конфигурация и переменные окружения
├── requirements.txt            # Зависимости Python
├── setup.py                    # Установочный скрипт
├── .env.example               # Пример конфигурации
├── Dockerfile                 # Docker образ
├── docker-compose.yml         # Docker Compose конфигурация
│
├── src/                       # Исходный код приложения
│   ├── __init__.py
│   │
│   ├── bot/                   # Логика Telegram бота
│   │   ├── __init__.py
│   │   ├── handlers.py        # Обработчики команд
│   │   ├── callbacks.py       # Обработчики callback кнопок
│   │   ├── states.py          # Состояния диалога
│   │   └── keyboards.py       # Клавиатуры и UI элементы
│   │
│   ├── processors/            # Обработка геоданных
│   │   ├── __init__.py
│   │   ├── point_cloud.py     # Работа с облаками точек
│   │   ├── tin_builder.py     # Построение триангуляции
│   │   ├── densifier.py       # Денсификация данных
│   │   └── coordinate_transformer.py  # Преобразование координат
│   │
│   ├── dxf/                   # Работа с DXF файлами
│   │   ├── __init__.py
│   │   ├── template_manager.py  # Управление шаблонами
│   │   ├── exporter.py        # Экспорт в DXF
│   │   ├── layer_manager.py   # Управление слоями
│   │   ├── block_inserter.py  # Вставка блоков
│   │   └── text_styler.py     # Работа с текстовыми стилями
│   │
│   ├── services/              # Бизнес-логика и сервисы
│   │   ├── __init__.py
│   │   ├── project_service.py # Управление проектами
│   │   ├── processing_service.py  # Оркестрация обработки
│   │   ├── file_service.py    # Работа с файлами
│   │   └── validation_service.py  # Валидация данных
│   │
│   ├── models/                # Модели данных
│   │   ├── __init__.py
│   │   ├── project.py         # Модель проекта
│   │   ├── point_data.py      # Модель точечных данных
│   │   ├── tin_model.py       # Модель TIN
│   │   └── settings.py        # Модель настроек
│   │
│   ├── utils/                 # Утилиты и хелперы
│   │   ├── __init__.py
│   │   ├── logger.py          # Логирование
│   │   ├── validators.py      # Валидаторы
│   │   ├── converters.py      # Конвертеры форматов
│   │   ├── math_utils.py      # Математические утилиты
│   │   └── file_utils.py      # Утилиты для файлов
│   │
│   └── database/              # База данных (опционально)
│       ├── __init__.py
│       ├── models.py          # ORM модели
│       ├── session.py         # Сессии БД
│       └── migrations/        # Миграции
│
├── templates/                 # DXF шаблоны
│   ├── basic.dxf
│   ├── gost.dxf
│   └── topo.dxf
│
├── tests/                     # Тесты
│   ├── __init__.py
│   ├── test_processors/       # Тесты процессоров
│   ├── test_dxf/             # Тесты DXF модулей
│   ├── test_services/        # Тесты сервисов
│   └── fixtures/             # Тестовые данные
│
├── docs/                      # Документация
└── scripts/                   # Вспомогательные скрипты
    ├── deploy.sh
    ├── backup.sh
    └── migrate.py
```

### Диаграмма компонентов

```
┌─────────────────────────────────────────────────────────────┐
│                      Telegram Bot API                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Bot Handlers Layer                        │
│  (handlers.py, callbacks.py, keyboards.py)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Services Layer                            │
│  (ProjectService, ProcessingService, FileService)           │
└─────┬──────────────────┬──────────────────┬─────────────────┘
      │                  │                  │
      ▼                  ▼                  ▼
┌───────────┐    ┌──────────────┐    ┌──────────────┐
│    DXF    │    │  Processors  │    │   Database   │
│  Module   │    │    Module    │    │   (Optional) │
└───────────┘    └──────────────┘    └──────────────┘
      │                  │                  
      │                  │                  
      ▼                  ▼                  
┌───────────────────────────────────┐      
│         Utils & Models            │      
└───────────────────────────────────┘      
```

## Модули и их ответственность

### 1. Bot Module (`src/bot/`)

**Ответственность**: Взаимодействие с Telegram Bot API, обработка команд пользователя

#### `handlers.py`

Обработчики команд бота:

```python
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

async def start_handler(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n"
        f"Я помогу обработать ваши геоданные."
    )

async def new_project_handler(update: Update, context: CallbackContext):
    """Обработчик команды /new - создание нового проекта"""
    context.user_data['state'] = 'AWAITING_FILE'
    await update.message.reply_text(
        "📊 Создание нового проекта\n"
        "Отправьте файл с координатами (.txt или .xyz)"
    )

async def file_received_handler(update: Update, context: CallbackContext):
    """Обработчик получения файла"""
    file = await update.message.document.get_file()
    file_path = f"temp/{file.file_id}.txt"
    await file.download_to_drive(file_path)
    
    # Передача в сервисный слой
    from src.services.file_service import FileService
    file_service = FileService()
    result = await file_service.process_uploaded_file(file_path)
    
    await update.message.reply_text(
        f"✅ Файл обработан: {result['points_count']} точек"
    )
```

#### `states.py`

Определение состояний диалога:

```python
from enum import Enum

class BotState(Enum):
    """Состояния диалога с пользователем"""
    IDLE = "idle"
    AWAITING_FILE = "awaiting_file"
    AWAITING_SCALE = "awaiting_scale"
    AWAITING_TEMPLATE = "awaiting_template"
    PROCESSING = "processing"
    READY_TO_EXPORT = "ready_to_export"

class ProjectStage(Enum):
    """Стадии обработки проекта"""
    CREATED = "created"
    DATA_LOADED = "data_loaded"
    TIN_BUILT = "tin_built"
    DENSIFIED = "densified"
    TEMPLATE_APPLIED = "template_applied"
    EXPORTED = "exported"
```

#### `keyboards.py`

UI элементы (клавиатуры):

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu_keyboard():
    """Главное меню"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Новый проект", callback_data="new_project"),
            InlineKeyboardButton("📈 Статус", callback_data="status")
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
            InlineKeyboardButton("📖 Помощь", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_processing_options_keyboard():
    """Опции обработки данных"""
    keyboard = [
        [InlineKeyboardButton("🔺 Построить TIN", callback_data="build_tin")],
        [InlineKeyboardButton("⚖️ Настроить масштаб", callback_data="set_scale")],
        [InlineKeyboardButton("📋 Загрузить шаблон", callback_data="upload_template")],
        [InlineKeyboardButton("🚀 Экспортировать", callback_data="export")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_densification_keyboard():
    """Опции денсификации"""
    keyboard = [
        [InlineKeyboardButton("2x плотность", callback_data="densify_2")],
        [InlineKeyboardButton("3x плотность", callback_data="densify_3")],
        [InlineKeyboardButton("Пропустить", callback_data="densify_skip")]
    ]
    return InlineKeyboardMarkup(keyboard)
```

### 2. Processors Module (`src/processors/`)

**Ответственность**: Обработка геопространственных данных

#### `point_cloud.py`

Работа с облаками точек:

```python
import numpy as np
from typing import Tuple, List
from dataclasses import dataclass

@dataclass
class PointCloud:
    """Модель облака точек"""
    points: np.ndarray  # Nx3 массив (X, Y, Z)
    attributes: dict = None
    
    @property
    def count(self) -> int:
        return len(self.points)
    
    @property
    def bounds(self) -> Tuple[float, float, float, float, float, float]:
        """Границы: (min_x, max_x, min_y, max_y, min_z, max_z)"""
        min_vals = self.points.min(axis=0)
        max_vals = self.points.max(axis=0)
        return (*min_vals, *max_vals)

class PointCloudProcessor:
    """Обработчик облаков точек"""
    
    def load_from_file(self, filepath: str) -> PointCloud:
        """Загрузка из файла"""
        points = self._parse_file(filepath)
        return PointCloud(points=points)
    
    def _parse_file(self, filepath: str) -> np.ndarray:
        """Парсинг файла с координатами"""
        points = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        x, y, z = map(float, parts[:3])
                        points.append([x, y, z])
                    except ValueError:
                        continue
        
        return np.array(points)
    
    def remove_duplicates(self, cloud: PointCloud, tolerance: float = 0.001) -> PointCloud:
        """Удаление дубликатов"""
        from scipy.spatial import cKDTree
        
        tree = cKDTree(cloud.points[:, :2])  # XY только
        unique_indices = []
        seen = set()
        
        for i, point in enumerate(cloud.points):
            if i not in seen:
                neighbors = tree.query_ball_point(point[:2], tolerance)
                unique_indices.append(i)
                seen.update(neighbors)
        
        return PointCloud(points=cloud.points[unique_indices])
    
    def filter_outliers(self, cloud: PointCloud, sigma: float = 3.0) -> PointCloud:
        """Фильтрация выбросов (метод 3 сигма)"""
        z_mean = cloud.points[:, 2].mean()
        z_std = cloud.points[:, 2].std()
        
        mask = np.abs(cloud.points[:, 2] - z_mean) <= sigma * z_std
        return PointCloud(points=cloud.points[mask])
    
    def thin_points(self, cloud: PointCloud, min_distance: float) -> PointCloud:
        """Прореживание точек"""
        from scipy.spatial import cKDTree
        
        tree = cKDTree(cloud.points[:, :2])
        keep_indices = [0]
        
        for i in range(1, cloud.count):
            distances, _ = tree.query(cloud.points[i, :2], k=2)
            if len(distances) > 1 and distances[1] >= min_distance:
                keep_indices.append(i)
        
        return PointCloud(points=cloud.points[keep_indices])
```

#### `tin_builder.py`

Построение триангуляции:

```python
import numpy as np
from scipy.spatial import Delaunay
from typing import Tuple, List

class TINBuilder:
    """Построитель триангуляционной нерегулярной сети"""
    
    def __init__(self, max_edge_length: float = None):
        self.max_edge_length = max_edge_length
    
    def build(self, points: np.ndarray) -> 'TIN':
        """Построение TIN методом Делоне"""
        # Триангуляция Делоне (только XY)
        tri = Delaunay(points[:, :2])
        
        # Фильтрация длинных рёбер
        triangles = self._filter_long_edges(points, tri.simplices)
        
        # Расчёт метрик качества
        quality = self._calculate_quality(points, triangles)
        
        return TIN(
            points=points,
            triangles=triangles,
            quality=quality
        )
    
    def _filter_long_edges(self, points: np.ndarray, 
                          triangles: np.ndarray) -> np.ndarray:
        """Фильтрация треугольников с длинными рёбрами"""
        if self.max_edge_length is None:
            return triangles
        
        valid_triangles = []
        for triangle in triangles:
            pts = points[triangle]
            # Проверка длин всех рёбер
            edge_lengths = [
                np.linalg.norm(pts[1, :2] - pts[0, :2]),
                np.linalg.norm(pts[2, :2] - pts[1, :2]),
                np.linalg.norm(pts[0, :2] - pts[2, :2])
            ]
            
            if max(edge_lengths) <= self.max_edge_length:
                valid_triangles.append(triangle)
        
        return np.array(valid_triangles)
    
    def _calculate_quality(self, points: np.ndarray, 
                          triangles: np.ndarray) -> float:
        """Расчёт среднего коэффициента качества треугольников"""
        qualities = []
        
        for triangle in triangles:
            pts = points[triangle, :2]
            
            # Площадь треугольника
            area = 0.5 * abs(
                pts[0, 0] * (pts[1, 1] - pts[2, 1]) +
                pts[1, 0] * (pts[2, 1] - pts[0, 1]) +
                pts[2, 0] * (pts[0, 1] - pts[1, 1])
            )
            
            # Длины рёбер
            edges = [
                np.linalg.norm(pts[1] - pts[0]),
                np.linalg.norm(pts[2] - pts[1]),
                np.linalg.norm(pts[0] - pts[2])
            ]
            
            # Коэффициент качества: 4*sqrt(3)*area / sum(edge^2)
            perimeter_sq = sum(e**2 for e in edges)
            quality = 4 * np.sqrt(3) * area / perimeter_sq if perimeter_sq > 0 else 0
            qualities.append(quality)
        
        return np.mean(qualities) if qualities else 0

class TIN:
    """Модель триангуляционной сети"""
    
    def __init__(self, points: np.ndarray, triangles: np.ndarray, quality: float):
        self.points = points
        self.triangles = triangles
        self.quality = quality
    
    @property
    def triangle_count(self) -> int:
        return len(self.triangles)
    
    def get_edges(self) -> List[Tuple[int, int]]:
        """Получение всех уникальных рёбер"""
        edges = set()
        for triangle in self.triangles:
            edges.add(tuple(sorted([triangle[0], triangle[1]])))
            edges.add(tuple(sorted([triangle[1], triangle[2]])))
            edges.add(tuple(sorted([triangle[2], triangle[0]])))
        return list(edges)
```

#### `densifier.py`

Денсификация данных:

```python
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from typing import Tuple

class Densifier:
    """Денсификатор облаков точек"""
    
    def densify(self, points: np.ndarray, tin: 'TIN', 
                factor: float = 2.0) -> np.ndarray:
        """
        Денсификация точек внутри треугольников TIN
        
        Args:
            points: Исходные точки
            tin: Триангуляция
            factor: Коэффициент увеличения плотности
        
        Returns:
            Расширенный массив точек
        """
        new_points = [points]
        
        # Создание интерполятора
        interpolator = LinearNDInterpolator(points[:, :2], points[:, 2])
        
        # Для каждого треугольника
        for triangle in tin.triangles:
            tri_points = points[triangle]
            
            # Генерация новых точек внутри треугольника
            interior_points = self._generate_interior_points(
                tri_points, factor
            )
            
            # Интерполяция Z координат
            z_values = interpolator(interior_points[:, 0], interior_points[:, 1])
            
            # Фильтрация NaN значений
            valid_mask = ~np.isnan(z_values)
            if valid_mask.any():
                new_coords = np.column_stack([
                    interior_points[valid_mask],
                    z_values[valid_mask]
                ])
                new_points.append(new_coords)
        
        return np.vstack(new_points)
    
    def _generate_interior_points(self, triangle: np.ndarray, 
                                  factor: float) -> np.ndarray:
        """Генерация точек внутри треугольника"""
        # Количество новых точек на основе фактора
        n_points = int((factor - 1) ** 2)
        
        if n_points == 0:
            return np.array([]).reshape(0, 2)
        
        # Генерация барицентрических координат
        points = []
        steps = int(np.sqrt(n_points)) + 1
        
        for i in range(1, steps):
            for j in range(1, steps - i):
                alpha = i / steps
                beta = j / steps
                gamma = 1 - alpha - beta
                
                if gamma > 0:
                    # Преобразование в декартовы координаты
                    x = (alpha * triangle[0, 0] + 
                         beta * triangle[1, 0] + 
                         gamma * triangle[2, 0])
                    y = (alpha * triangle[0, 1] + 
                         beta * triangle[1, 1] + 
                         gamma * triangle[2, 1])
                    points.append([x, y])
        
        return np.array(points) if points else np.array([]).reshape(0, 2)
```

### 3. DXF Module (`src/dxf/`)

**Ответственность**: Работа с DXF файлами

#### `exporter.py`

Экспорт в DXF:

```python
import ezdxf
from ezdxf.document import Drawing
import numpy as np
from typing import Optional

class DXFExporter:
    """Экспортер в DXF формат"""
    
    def __init__(self, template_path: Optional[str] = None):
        if template_path:
            self.doc = ezdxf.readfile(template_path)
        else:
            self.doc = ezdxf.new('R2018')
        
        self.msp = self.doc.modelspace()
    
    def export_tin(self, tin: 'TIN', layer: str = 'TIN'):
        """Экспорт TIN как линий"""
        edges = tin.get_edges()
        
        for edge in edges:
            p1 = tin.points[edge[0]]
            p2 = tin.points[edge[1]]
            
            self.msp.add_line(
                start=(p1[0], p1[1]),
                end=(p2[0], p2[1]),
                dxfattribs={'layer': layer}
            )
    
    def export_points(self, points: np.ndarray, layer: str = 'POINTS',
                     block_name: str = 'POINT_MARKER'):
        """Экспорт точек как блоков"""
        for point in points:
            self.msp.add_blockref(
                block_name,
                insert=(point[0], point[1]),
                dxfattribs={'layer': layer}
            )
    
    def add_labels(self, points: np.ndarray, layer: str = 'LABELS',
                  style: str = 'COORDINATES', height: float = 0.3):
        """Добавление подписей высот"""
        for point in points:
            self.msp.add_text(
                f"{point[2]:.3f}",
                dxfattribs={
                    'layer': layer,
                    'style': style,
                    'height': height,
                    'insert': (point[0], point[1] - 1.0)
                }
            )
    
    def save(self, filepath: str):
        """Сохранение DXF файла"""
        self.doc.saveas(filepath)
```

### 4. Services Module (`src/services/`)

**Ответственность**: Бизнес-логика, оркестрация операций

#### `processing_service.py`

Оркестрация обработки:

```python
from src.processors.point_cloud import PointCloudProcessor, PointCloud
from src.processors.tin_builder import TINBuilder
from src.processors.densifier import Densifier
from src.dxf.exporter import DXFExporter
from src.models.project import Project
from typing import Dict, Any

class ProcessingService:
    """Сервис обработки геоданных"""
    
    def __init__(self):
        self.point_processor = PointCloudProcessor()
        self.tin_builder = TINBuilder()
        self.densifier = Densifier()
    
    async def process_project(self, project: Project) -> Dict[str, Any]:
        """Полная обработка проекта"""
        results = {}
        
        # 1. Загрузка и очистка данных
        cloud = self.point_processor.load_from_file(project.data_file)
        cloud = self.point_processor.remove_duplicates(cloud)
        cloud = self.point_processor.filter_outliers(cloud)
        results['points_loaded'] = cloud.count
        
        # 2. Построение TIN
        tin = self.tin_builder.build(cloud.points)
        results['triangles'] = tin.triangle_count
        results['tin_quality'] = tin.quality
        
        # 3. Денсификация (если требуется)
        if project.settings.densify_factor > 1.0:
            densified_points = self.densifier.densify(
                cloud.points, tin, project.settings.densify_factor
            )
            tin = self.tin_builder.build(densified_points)
            results['points_after_densification'] = len(densified_points)
        
        # 4. Экспорт в DXF
        exporter = DXFExporter(project.template_path)
        exporter.export_tin(tin, layer='TIN')
        exporter.export_points(cloud.points, layer='POINTS')
        exporter.add_labels(cloud.points, layer='LABELS')
        
        output_path = f"output/project_{project.id}.dxf"
        exporter.save(output_path)
        results['output_file'] = output_path
        
        return results
```

## Сервисная архитектура

### Dependency Injection

Используем паттерн внедрения зависимостей:

```python
# src/services/__init__.py

from typing import Optional

class ServiceContainer:
    """Контейнер сервисов"""
    
    _instance: Optional['ServiceContainer'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Инициализация сервисов"""
        from src.services.processing_service import ProcessingService
        from src.services.project_service import ProjectService
        from src.services.file_service import FileService
        
        self.processing = ProcessingService()
        self.project = ProjectService()
        self.file = FileService()
    
    @classmethod
    def get(cls) -> 'ServiceContainer':
        """Получение экземпляра контейнера"""
        return cls()

# Использование в коде
services = ServiceContainer.get()
result = await services.processing.process_project(project)
```

## Добавление новых кодов и блоков

### Добавление нового блока в DXF

**Шаг 1: Определение блока**

```python
# src/dxf/blocks.py

from ezdxf.document import Drawing

class CustomBlockDefinitions:
    """Определения пользовательских блоков"""
    
    @staticmethod
    def add_benchmark_block(doc: Drawing):
        """Добавление блока репера"""
        block = doc.blocks.new(name='BENCHMARK')
        
        # Квадрат
        block.add_lwpolyline([
            (-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)
        ], close=True, dxfattribs={'layer': 'POINTS'})
        
        # Крест внутри
        block.add_line((-0.5, 0), (0.5, 0), dxfattribs={'layer': 'POINTS'})
        block.add_line((0, -0.5), (0, 0.5), dxfattribs={'layer': 'POINTS'})
        
        # Атрибут высоты
        block.add_attdef(
            tag='ELEVATION',
            text='0.000',
            dxfattribs={
                'layer': 'LABELS',
                'height': 0.3,
                'insert': (0, -1.0)
            }
        )
        
        # Атрибут номера
        block.add_attdef(
            tag='NUMBER',
            text='RP-1',
            dxfattribs={
                'layer': 'LABELS',
                'height': 0.3,
                'insert': (0, 0.7)
            }
        )
```

**Шаг 2: Регистрация в системе**

```python
# src/dxf/template_manager.py

class TemplateManager:
    
    def register_custom_blocks(self, doc: Drawing):
        """Регистрация пользовательских блоков"""
        from src.dxf.blocks import CustomBlockDefinitions
        
        CustomBlockDefinitions.add_benchmark_block(doc)
        # Добавить другие блоки...
```

**Шаг 3: Использование блока**

```python
# src/processors/point_classifier.py

class PointClassifier:
    """Классификатор точек по кодам"""
    
    CODE_MAPPING = {
        '101': 'POINT_MARKER',      # Обычная точка
        '102': 'BENCHMARK',          # Репер
        '103': 'TREE',              # Дерево
        '104': 'POLE',              # Столб
    }
    
    def get_block_for_code(self, code: str) -> str:
        """Получение имени блока для кода"""
        return self.CODE_MAPPING.get(code, 'POINT_MARKER')
```

### Добавление обработки нового типа кода

**Пример: Обработка кодов растительности**

```python
# src/processors/vegetation_processor.py

from typing import List, Tuple
import numpy as np

class VegetationProcessor:
    """Обработчик данных растительности"""
    
    TREE_CODES = ['103', '104', '105']  # Различные типы деревьев
    SHRUB_CODES = ['201', '202']        # Кустарники
    
    def extract_vegetation(self, points: np.ndarray, 
                          codes: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Извлечение точек растительности"""
        tree_mask = np.isin(codes, self.TREE_CODES)
        shrub_mask = np.isin(codes, self.SHRUB_CODES)
        
        trees = points[tree_mask]
        shrubs = points[shrub_mask]
        
        return trees, shrubs
    
    def generate_tree_canopy(self, tree_point: np.ndarray,
                            radius: float = 3.0) -> List[Tuple[float, float]]:
        """Генерация полигона кроны дерева"""
        x, y = tree_point[:2]
        n_segments = 16
        
        angles = np.linspace(0, 2 * np.pi, n_segments, endpoint=False)
        canopy = [(x + radius * np.cos(a), y + radius * np.sin(a)) 
                  for a in angles]
        
        return canopy
```

**Интеграция в экспорт:**

```python
# В DXFExporter добавить метод:

def export_vegetation(self, trees: np.ndarray, shrubs: np.ndarray):
    """Экспорт растительности"""
    veg_processor = VegetationProcessor()
    
    # Экспорт деревьев с кронами
    for tree in trees:
        # Вставка блока дерева
        self.msp.add_blockref(
            'TREE',
            insert=(tree[0], tree[1]),
            dxfattribs={'layer': 'VEGETATION'}
        )
        
        # Добавление полигона кроны
        canopy = veg_processor.generate_tree_canopy(tree)
        self.msp.add_lwpolyline(
            canopy,
            close=True,
            dxfattribs={'layer': 'VEGETATION', 'color': 3}  # Зелёный
        )
```

## Расширение функциональности

### Добавление нового формата входных данных

**Пример: Поддержка LAS файлов (LiDAR)**

```python
# src/processors/las_reader.py

import laspy
import numpy as np

class LASReader:
    """Читатель LAS файлов"""
    
    def read(self, filepath: str, classification: int = None) -> np.ndarray:
        """
        Чтение LAS файла
        
        Args:
            filepath: Путь к LAS файлу
            classification: Фильтр по классификации (2 = ground)
        
        Returns:
            Массив точек (X, Y, Z)
        """
        las = laspy.read(filepath)
        
        # Извлечение координат
        x = las.x
        y = las.y
        z = las.z
        
        # Фильтрация по классификации
        if classification is not None:
            mask = las.classification == classification
            x, y, z = x[mask], y[mask], z[mask]
        
        return np.column_stack([x, y, z])
```

**Регистрация в FileService:**

```python
# src/services/file_service.py

class FileService:
    
    SUPPORTED_FORMATS = {
        '.txt': 'text',
        '.xyz': 'text',
        '.las': 'las',
        '.laz': 'las',  # Сжатый LAS
    }
    
    def load_file(self, filepath: str) -> np.ndarray:
        """Загрузка файла с автоопределением формата"""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {ext}")
        
        format_type = self.SUPPORTED_FORMATS[ext]
        
        if format_type == 'text':
            processor = PointCloudProcessor()
            cloud = processor.load_from_file(filepath)
            return cloud.points
        elif format_type == 'las':
            reader = LASReader()
            return reader.read(filepath, classification=2)  # Ground points
```

### Добавление нового метода триангуляции

**Пример: Constrained Delaunay Triangulation**

```python
# src/processors/constrained_tin.py

from shapely.geometry import Polygon
from scipy.spatial import Delaunay
import numpy as np

class ConstrainedTINBuilder(TINBuilder):
    """Построитель TIN с учётом границ"""
    
    def __init__(self, boundary: Polygon = None, **kwargs):
        super().__init__(**kwargs)
        self.boundary = boundary
    
    def build(self, points: np.ndarray) -> 'TIN':
        """Построение с учётом границ"""
        # Базовая триангуляция
        tin = super().build(points)
        
        # Фильтрация треугольников вне границы
        if self.boundary:
            tin.triangles = self._filter_by_boundary(
                points, tin.triangles, self.boundary
            )
        
        return tin
    
    def _filter_by_boundary(self, points: np.ndarray,
                           triangles: np.ndarray,
                           boundary: Polygon) -> np.ndarray:
        """Фильтрация треугольников вне полигона"""
        from shapely.geometry import Point
        
        valid_triangles = []
        
        for triangle in triangles:
            # Центроид треугольника
            centroid = points[triangle, :2].mean(axis=0)
            
            if boundary.contains(Point(centroid)):
                valid_triangles.append(triangle)
        
        return np.array(valid_triangles)
```

## Тестирование

### Структура тестов

```python
# tests/test_processors/test_tin_builder.py

import pytest
import numpy as np
from src.processors.tin_builder import TINBuilder

class TestTINBuilder:
    """Тесты построителя TIN"""
    
    @pytest.fixture
    def sample_points(self):
        """Тестовые точки"""
        return np.array([
            [0, 0, 100],
            [10, 0, 101],
            [10, 10, 102],
            [0, 10, 103],
            [5, 5, 104]
        ])
    
    def test_build_basic_tin(self, sample_points):
        """Тест базового построения TIN"""
        builder = TINBuilder()
        tin = builder.build(sample_points)
        
        assert tin.triangle_count > 0
        assert tin.quality > 0
        assert len(tin.points) == len(sample_points)
    
    def test_filter_long_edges(self, sample_points):
        """Тест фильтрации длинных рёбер"""
        builder = TINBuilder(max_edge_length=10.0)
        tin = builder.build(sample_points)
        
        # Проверка, что все рёбра короче максимума
        for edge in tin.get_edges():
            p1, p2 = tin.points[edge[0]], tin.points[edge[1]]
            length = np.linalg.norm(p2[:2] - p1[:2])
            assert length <= 10.0
    
    def test_quality_calculation(self, sample_points):
        """Тест расчёта качества"""
        builder = TINBuilder()
        tin = builder.build(sample_points)
        
        assert 0 <= tin.quality <= 1
```

### Интеграционные тесты

```python
# tests/test_integration/test_full_workflow.py

import pytest
from src.services.processing_service import ProcessingService
from src.models.project import Project, ProjectSettings

@pytest.mark.asyncio
class TestFullWorkflow:
    """Интеграционные тесты полного цикла"""
    
    async def test_complete_processing_pipeline(self, tmp_path):
        """Тест полного цикла обработки"""
        # Подготовка тестовых данных
        data_file = tmp_path / "test_data.txt"
        data_file.write_text("""
        X Y Z
        1000 2000 150
        1001 2000 151
        1001 2001 152
        1000 2001 153
        """)
        
        # Создание проекта
        project = Project(
            id="test_001",
            data_file=str(data_file),
            settings=ProjectSettings(
                scale=1000,
                densify_factor=2.0
            )
        )
        
        # Обработка
        service = ProcessingService()
        results = await service.process_project(project)
        
        # Проверки
        assert results['points_loaded'] >= 4
        assert results['triangles'] > 0
        assert 'output_file' in results
```

## Стандарты кодирования

### Python Style Guide

Следуем PEP 8 и дополнительным правилам:

```python
# Docstrings в формате Google Style

def calculate_area(points: np.ndarray) -> float:
    """
    Вычисление площади полигона.
    
    Args:
        points: Массив координат вершин (Nx2)
    
    Returns:
        Площадь полигона в квадратных единицах
    
    Raises:
        ValueError: Если точек меньше 3
    
    Example:
        >>> points = np.array([[0, 0], [1, 0], [0, 1]])
        >>> calculate_area(points)
        0.5
    """
    if len(points) < 3:
        raise ValueError("Polygon must have at least 3 points")
    
    # Формула площади Гаусса
    x = points[:, 0]
    y = points[:, 1]
    return 0.5 * abs(sum(x[i] * y[i+1] - x[i+1] * y[i] 
                        for i in range(-1, len(points)-1)))
```

### Type Hints

Всегда используем аннотации типов:

```python
from typing import List, Tuple, Optional, Union, Dict, Any
import numpy as np
from numpy.typing import NDArray

def process_coordinates(
    coords: NDArray[np.float64],
    transform: Optional[np.ndarray] = None,
    precision: int = 3
) -> Tuple[NDArray[np.float64], Dict[str, Any]]:
    """Обработка координат с опциональным преобразованием"""
    ...
```

### Логирование

```python
import logging

logger = logging.getLogger(__name__)

def process_large_dataset(data: np.ndarray):
    """Обработка большого набора данных"""
    logger.info(f"Starting processing of {len(data)} points")
    
    try:
        result = heavy_computation(data)
        logger.info(f"Processing complete, result size: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        raise
```

---

[← Руководство пользователя](./user-guide.md) | [Развертывание →](./deployment.md)
