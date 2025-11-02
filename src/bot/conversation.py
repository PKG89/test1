"""Conversation handlers for densification configuration."""

from typing import Dict, Any
from src.models.settings import DensificationSettings, InterpolationMethod


class DensificationConversation:
    """Manages conversation flow for densification settings."""
    
    @staticmethod
    def get_initial_prompt() -> str:
        """Get initial prompt for densification configuration."""
        return (
            "🔧 **Настройка денсификации рельефа**\n\n"
            "Денсификация позволяет автоматически добавить точки в разреженных областях "
            "для улучшения детализации поверхности.\n\n"
            "Хотите включить денсификацию?\n\n"
            "✅ Да - настроить параметры\n"
            "⏭️ Нет - пропустить и продолжить\n"
        )
    
    @staticmethod
    def get_grid_spacing_prompt(current_spacing: float = 5.0) -> str:
        """Get prompt for grid spacing configuration."""
        return (
            f"📏 **Шаг сетки (Grid Spacing)**\n\n"
            f"Текущее значение: {current_spacing} м\n\n"
            f"Укажите шаг сетки для генерации новых точек (в метрах).\n"
            f"Рекомендуемое значение: 5-10 м\n\n"
            f"Введите число или выберите:\n"
            f"• 3 м - высокая плотность\n"
            f"• 5 м - средняя плотность (по умолчанию)\n"
            f"• 10 м - низкая плотность\n"
        )
    
    @staticmethod
    def get_interpolation_method_prompt() -> str:
        """Get prompt for interpolation method selection."""
        return (
            "🔬 **Метод интерполяции**\n\n"
            "Выберите метод интерполяции для вычисления высот новых точек:\n\n"
            "🔹 **Linear** (Линейный) - быстрый, подходит для большинства случаев\n"
            "   Использует линейную интерполяцию внутри треугольников TIN\n\n"
            "🔹 **Cubic** (Кубический) - более гладкие поверхности\n"
            "   Использует интерполяцию высшего порядка\n\n"
            "🔹 **Nearest** (Ближайший) - сохраняет исходные значения\n"
            "   Копирует значение ближайшей точки\n\n"
            "💡 Рекомендуется: Linear (по умолчанию)\n"
        )
    
    @staticmethod
    def get_layer_visibility_prompt() -> str:
        """Get prompt for layer visibility configuration."""
        return (
            "👁️ **Видимость слоёв**\n\n"
            "Выберите, какие слои включить в итоговый DXF:\n\n"
            "🔺 **Слой треугольников** ('2 отредактированная поверхность')\n"
            "   Треугольники TIN с добавленными точками\n\n"
            "📍 **Слой точек** ('2 пикеты добавленные')\n"
            "   Сгенерированные точки (красные треугольники)\n\n"
            "Выберите:\n"
            "• Оба слоя (рекомендуется)\n"
            "• Только треугольники\n"
            "• Только точки\n"
        )
    
    @staticmethod
    def get_summary(settings: DensificationSettings) -> str:
        """Get summary of configured settings."""
        return (
            "📋 **Итоговые настройки денсификации**\n\n"
            f"✓ Денсификация: {'Включена' if settings.enabled else 'Выключена'}\n"
            f"✓ Шаг сетки: {settings.grid_spacing} м\n"
            f"✓ Метод интерполяции: {settings.interpolation_method.value}\n"
            f"✓ Порог разреженности: {settings.min_spacing_threshold} м\n"
            f"✓ Максимум точек: {settings.max_points}\n"
            f"✓ Слой треугольников: {'Показать' if settings.show_triangles_layer else 'Скрыть'}\n"
            f"✓ Слой точек: {'Показать' if settings.show_generated_layer else 'Скрыть'}\n\n"
            "Продолжить обработку с этими настройками?\n"
        )
    
    @staticmethod
    def parse_grid_spacing(user_input: str) -> float:
        """Parse user input for grid spacing."""
        try:
            value = float(user_input)
            if value <= 0:
                return 5.0
            return min(value, 100.0)
        except ValueError:
            return 5.0
    
    @staticmethod
    def parse_interpolation_method(user_input: str) -> InterpolationMethod:
        """Parse user input for interpolation method."""
        input_lower = user_input.lower()
        if 'cubic' in input_lower or 'кубич' in input_lower:
            return InterpolationMethod.CUBIC
        elif 'nearest' in input_lower or 'ближайш' in input_lower:
            return InterpolationMethod.NEAREST
        else:
            return InterpolationMethod.LINEAR
    
    @staticmethod
    def parse_layer_visibility(user_input: str) -> Dict[str, bool]:
        """Parse user input for layer visibility."""
        input_lower = user_input.lower()
        
        if 'оба' in input_lower or 'both' in input_lower or 'все' in input_lower:
            return {'triangles': True, 'points': True}
        elif 'треуг' in input_lower or 'triangle' in input_lower:
            return {'triangles': True, 'points': False}
        elif 'точ' in input_lower or 'point' in input_lower:
            return {'triangles': False, 'points': True}
        else:
            return {'triangles': True, 'points': True}
    
    @staticmethod
    def get_processing_message(stats: Dict[str, Any]) -> str:
        """Get message about processing results."""
        if stats.get('skipped', False):
            return "⏭️ Денсификация пропущена."
        
        original = stats.get('original_points', 0)
        generated = stats.get('generated_points', 0)
        regions = stats.get('sparse_regions_found', 0)
        
        message = f"✅ **Денсификация завершена**\n\n"
        message += f"📊 Исходных точек: {original}\n"
        message += f"➕ Добавлено точек: {generated}\n"
        message += f"🔍 Найдено разреженных областей: {regions}\n"
        
        if stats.get('limited_by_max', False):
            message += f"\n⚠️ Ограничено максимальным количеством точек\n"
        
        if generated > 0:
            percentage = (generated / original) * 100
            message += f"\n📈 Увеличение плотности: +{percentage:.1f}%\n"
        
        return message
    
    @staticmethod
    def get_defaults_documentation() -> str:
        """Get documentation for default settings."""
        return (
            "📖 **Параметры денсификации по умолчанию**\n\n"
            "**Шаг сетки (Grid Spacing):** 5.0 м\n"
            "  Расстояние между генерируемыми точками\n\n"
            "**Метод интерполяции:** Linear (Линейный)\n"
            "  Метод вычисления высот для новых точек\n\n"
            "**Порог разреженности:** 10.0 м\n"
            "  Минимальное расстояние для активации денсификации\n\n"
            "**Максимум точек:** 10000\n"
            "  Ограничение для предотвращения избыточной генерации\n\n"
            "**Видимость слоёв:** Оба включены\n"
            "  - '2 отредактированная поверхность' (треугольники)\n"
            "  - '2 пикеты добавленные' (точки/метки)\n\n"
            "**Стилизация:**\n"
            "  - Сгенерированные точки: красные треугольники\n"
            "  - Аннотации: текст с высотными отметками\n"
        )
