"""Conversation handlers for densification and TIN configuration."""

from typing import Dict, Any, List
from src.models.settings import DensificationSettings, InterpolationMethod, TINSettings, TINCodeSelection


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


class TINConversation:
    """Manages conversation flow for TIN configuration."""
    
    @staticmethod
    def get_initial_prompt() -> str:
        """Get initial prompt for TIN configuration."""
        return (
            "🔺 **Настройка построения TIN (триангуляция)**\n\n"
            "TIN (Triangulated Irregular Network) - триангуляционная нерегулярная сеть "
            "для моделирования поверхности рельефа.\n\n"
            "Хотите настроить построение TIN с учётом структурных линий?\n\n"
            "✅ Да - настроить параметры\n"
            "⏭️ Нет - использовать стандартные настройки\n"
        )
    
    @staticmethod
    def get_code_selection_prompt() -> str:
        """Get prompt for point code selection."""
        return (
            "📋 **Выбор кодов точек для TIN**\n\n"
            "Выберите, какие коды точек использовать для построения TIN:\n\n"
            "🔹 **Все точки** (по умолчанию)\n"
            "   Использовать все точки из файла\n\n"
            "🔹 **Только рельеф**\n"
            "   Использовать только точки рельефа (terrain)\n\n"
            "🔹 **С учётом структурных линий**\n"
            "   Включить bpl, cpl, bord для более точного моделирования\n\n"
            "🔹 **Пользовательский набор**\n"
            "   Указать собственный список кодов\n\n"
            "Введите: все / рельеф / линии / пользовательский\n"
        )
    
    @staticmethod
    def get_custom_codes_prompt() -> str:
        """Get prompt for custom code input."""
        return (
            "📝 **Пользовательские коды**\n\n"
            "Введите коды точек через запятую.\n"
            "Например: bpl, cpl, terrain, bord\n\n"
            "Доступные типы кодов:\n"
            "• bpl - линии разрывов (breaklines)\n"
            "• cpl - осевые линии (centerlines)\n"
            "• bord - границы (borders)\n"
            "• terrain - точки рельефа\n"
            "• other - прочие точки\n"
        )
    
    @staticmethod
    def get_breaklines_prompt() -> str:
        """Get prompt for breaklines configuration."""
        return (
            "🔗 **Структурные линии (Breaklines)**\n\n"
            "Структурные линии (breaklines) - это линии разрывов, границ и других "
            "важных объектов, которые должны соблюдаться при триангуляции.\n\n"
            "Включить поддержку структурных линий?\n\n"
            "✅ Да - учитывать при построении TIN\n"
            "❌ Нет - простая триангуляция\n\n"
            "💡 Рекомендуется: Да (для более точного моделирования)\n"
        )
    
    @staticmethod
    def get_breakline_codes_prompt(default_codes: List[str]) -> str:
        """Get prompt for breakline code selection."""
        codes_str = ", ".join(default_codes)
        return (
            f"📌 **Коды структурных линий**\n\n"
            f"Текущие коды: {codes_str}\n\n"
            f"Укажите коды, которые представляют структурные линии.\n"
            f"Введите коды через запятую или оставьте по умолчанию.\n\n"
            f"Типичные коды:\n"
            f"• bpl - breaklines (линии разрывов)\n"
            f"• cpl - centerlines (осевые линии)\n"
            f"• bord - borders (границы)\n"
        )
    
    @staticmethod
    def get_output_layers_prompt() -> str:
        """Get prompt for output layers configuration."""
        return (
            "📄 **Выходные слои DXF**\n\n"
            "Включить слои с результатами TIN в итоговый DXF?\n\n"
            "Будут созданы слои:\n"
            "• '1 реальная поверхность' - треугольники TIN\n"
            "• '1 Отметки и точки реального рельефа' - точки и высотные отметки\n\n"
            "✅ Да - включить слои (рекомендуется)\n"
            "❌ Нет - пропустить\n"
        )
    
    @staticmethod
    def get_summary(settings: TINSettings) -> str:
        """Get summary of configured TIN settings."""
        code_selection_map = {
            TINCodeSelection.ALL: "Все точки",
            TINCodeSelection.TERRAIN_ONLY: "Только рельеф",
            TINCodeSelection.WITH_BREAKLINES: "С учётом структурных линий",
            TINCodeSelection.CUSTOM: "Пользовательский набор"
        }
        
        codes = ", ".join(settings.custom_codes) if settings.custom_codes else "не указаны"
        breakline_codes = ", ".join(settings.breakline_codes) if settings.breakline_codes else "не указаны"
        
        return (
            "📋 **Итоговые настройки TIN**\n\n"
            f"✓ Построение TIN: {'Включено' if settings.enabled else 'Выключено'}\n"
            f"✓ Выбор кодов: {code_selection_map.get(settings.code_selection, 'Все')}\n"
            f"✓ Коды точек: {codes}\n"
            f"✓ Структурные линии: {'Включены' if settings.use_breaklines else 'Выключены'}\n"
            f"✓ Коды breaklines: {breakline_codes}\n"
            f"✓ Выходные слои: {'Включены' if settings.output_layers else 'Выключены'}\n\n"
            "Продолжить с этими настройками?\n"
        )
    
    @staticmethod
    def parse_code_selection(user_input: str) -> TINCodeSelection:
        """Parse user input for code selection."""
        input_lower = user_input.lower()
        if 'рельеф' in input_lower or 'terrain' in input_lower:
            return TINCodeSelection.TERRAIN_ONLY
        elif 'лини' in input_lower or 'breakline' in input_lower:
            return TINCodeSelection.WITH_BREAKLINES
        elif 'пользов' in input_lower or 'custom' in input_lower:
            return TINCodeSelection.CUSTOM
        else:
            return TINCodeSelection.ALL
    
    @staticmethod
    def parse_custom_codes(user_input: str) -> List[str]:
        """Parse user input for custom codes."""
        codes = [code.strip().lower() for code in user_input.split(',')]
        return [code for code in codes if code]
    
    @staticmethod
    def parse_boolean(user_input: str) -> bool:
        """Parse user input for boolean choice."""
        input_lower = user_input.lower()
        return 'да' in input_lower or 'yes' in input_lower or input_lower.startswith('y')
    
    @staticmethod
    def get_processing_message(stats: Dict[str, Any]) -> str:
        """Get message about TIN processing results."""
        if stats.get('skipped', False):
            return "⏭️ Построение TIN пропущено."
        
        triangles = stats.get('triangle_count', 0)
        breaklines = stats.get('breakline_count', 0)
        quality = stats.get('quality', 0.0)
        
        message = f"✅ **TIN построен успешно**\n\n"
        message += f"🔺 Треугольников: {triangles}\n"
        message += f"📊 Качество триангуляции: {quality:.3f}\n"
        
        if breaklines > 0:
            message += f"🔗 Структурных линий учтено: {breaklines}\n"
        
        return message
