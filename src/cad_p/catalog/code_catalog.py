"""Comprehensive catalog mapping 60+ survey codes to canonical block names and rules."""

from typing import Dict, List, Optional
from src.models.rule_data import (
    CodeRule, RuleType, CommentHandling, BlockPlacement
)


class CodeCatalog:
    """Catalog of survey codes with comprehensive rule definitions."""
    
    def __init__(self):
        """Initialize the code catalog with all survey codes."""
        self._rules: Dict[str, CodeRule] = {}
        self._alias_map: Dict[str, str] = {}
        self._initialize_catalog()
    
    def _initialize_catalog(self):
        """Initialize all code definitions."""
        rules = [
            # Standard numbered points (№-rule)
            CodeRule(
                code="1",
                canonical_name="точка1",
                aliases=["т1", "tochka1", "t1"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=7
            ),
            CodeRule(
                code="2",
                canonical_name="точка2",
                aliases=["т2", "tochka2", "t2"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=7
            ),
            CodeRule(
                code="3",
                canonical_name="точка3",
                aliases=["т3", "tochka3", "t3"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=3
            ),
            CodeRule(
                code="4",
                canonical_name="точка4",
                aliases=["т4", "tochka4", "t4"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=4
            ),
            CodeRule(
                code="5",
                canonical_name="точка5",
                aliases=["т5", "tochka5", "t5"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=5
            ),
            
            # Kilometer markers (km-rule)
            CodeRule(
                code="km",
                canonical_name="километр",
                aliases=["KM", "км", "КМ", "kilometer"],
                rule_type=RuleType.KM_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="KM_MARKER", layer="BLOCKS"),
                text_layer="TEXT_KM",
                generate_label=True,
                label_format="км{number}",
                fallback_label="кмб/н",
                color=2
            ),
            CodeRule(
                code="km+",
                canonical_name="пикет",
                aliases=["KM+", "км+", "КМ+", "piket", "пк"],
                rule_type=RuleType.KM_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="PIKET", layer="BLOCKS"),
                text_layer="TEXT_KM",
                generate_label=True,
                label_format="пк{number}",
                fallback_label="пкб/н",
                color=2
            ),
            
            # Reference points (VK-rule)
            CodeRule(
                code="vk",
                canonical_name="высотная_точка",
                aliases=["VK", "ВК", "вк", "reper"],
                rule_type=RuleType.VK_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="VK_POINT", layer="VK"),
                text_layer="VK",
                generate_label=True,
                label_format="ВК{number}",
                fallback_label="ВКб/н",
                color=1
            ),
            CodeRule(
                code="rp",
                canonical_name="репер",
                aliases=["RP", "РП", "рп", "reper"],
                rule_type=RuleType.VK_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="REPER", layer="VK"),
                text_layer="VK",
                generate_label=True,
                label_format="Рп{number}",
                fallback_label="Рпб/н",
                color=1
            ),
            
            # Archaeological/Cultural objects - special handling
            CodeRule(
                code="shurf",
                canonical_name="шурф",
                aliases=["shurf", "шурф", "ШУРФ", "sh"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SPECIAL,
                block=BlockPlacement(block_name="SHURF", layer="BLOCKS_ARCH"),
                text_layer="TEXT_ARCH",
                generate_label=True,
                label_format="Ш{number}",
                fallback_label="Шб/н",
                color=6,
                special_behavior="three_labels",
                metadata={"label_count": 3}
            ),
            CodeRule(
                code="skulpt",
                canonical_name="скульптура",
                aliases=["skulpt", "скульп", "СКУЛЬП"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.BLOCK_LAYER,
                block=BlockPlacement(block_name="SKULPT", layer="BLOCKS_ARCH"),
                text_layer="BLOCKS_ARCH",
                comment_layer="BLOCKS_ARCH",
                generate_label=False,
                color=5
            ),
            CodeRule(
                code="eskizRAZR",
                canonical_name="эскиз_разрушения",
                aliases=["eskizrazr", "эскизразр", "razr"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.BLOCK_LAYER,
                block=BlockPlacement(block_name="ESKIZ_RAZR", layer="BLOCKS_ARCH"),
                text_layer="BLOCKS_ARCH",
                comment_layer="BLOCKS_ARCH",
                generate_label=False,
                color=1
            ),
            
            # Communication/utility codes (k-codes) - custom layers
            CodeRule(
                code="k-kabel",
                canonical_name="кабель",
                aliases=["kkabel", "кабель", "cable", "k-cable"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SPECIAL,
                block=BlockPlacement(block_name="KABEL", layer="K_KABEL"),
                text_layer="K_KABEL_TEXT",
                comment_layer="K_KABEL_TEXT",
                generate_label=True,
                label_format="К{number}",
                fallback_label="Кб/н",
                color=4,
                special_behavior="k_code_layer"
            ),
            CodeRule(
                code="k-tep",
                canonical_name="теплотрасса",
                aliases=["ktep", "тепло", "heat", "k-heat"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SPECIAL,
                block=BlockPlacement(block_name="TEPLO", layer="K_TEPLO"),
                text_layer="K_TEPLO_TEXT",
                comment_layer="K_TEPLO_TEXT",
                generate_label=True,
                label_format="Т{number}",
                fallback_label="Тб/н",
                color=1,
                special_behavior="k_code_layer"
            ),
            CodeRule(
                code="k-voda",
                canonical_name="водопровод",
                aliases=["kvoda", "вода", "water", "k-water"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SPECIAL,
                block=BlockPlacement(block_name="VODA", layer="K_VODA"),
                text_layer="K_VODA_TEXT",
                comment_layer="K_VODA_TEXT",
                generate_label=True,
                label_format="В{number}",
                fallback_label="Вб/н",
                color=5,
                special_behavior="k_code_layer"
            ),
            CodeRule(
                code="k-kanal",
                canonical_name="канализация",
                aliases=["kkanal", "канал", "sewer", "k-sewer"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SPECIAL,
                block=BlockPlacement(block_name="KANAL", layer="K_KANAL"),
                text_layer="K_KANAL_TEXT",
                comment_layer="K_KANAL_TEXT",
                generate_label=True,
                label_format="Кн{number}",
                fallback_label="Кнб/н",
                color=3,
                special_behavior="k_code_layer"
            ),
            CodeRule(
                code="k-gaz",
                canonical_name="газопровод",
                aliases=["kgaz", "газ", "gas", "k-gas"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SPECIAL,
                block=BlockPlacement(block_name="GAZ", layer="K_GAZ"),
                text_layer="K_GAZ_TEXT",
                comment_layer="K_GAZ_TEXT",
                generate_label=True,
                label_format="Г{number}",
                fallback_label="Гб/н",
                color=6,
                special_behavior="k_code_layer"
            ),
            
            # Building/structure codes
            CodeRule(
                code="zd",
                canonical_name="здание",
                aliases=["ZD", "зд", "ЗД", "building"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="ZDANIE", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="ЗД{number}",
                fallback_label="ЗДб/н",
                color=7
            ),
            CodeRule(
                code="str",
                canonical_name="строение",
                aliases=["STR", "стр", "СТР", "structure"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="STROENIE", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="Стр{number}",
                fallback_label="Стрб/н",
                color=7
            ),
            CodeRule(
                code="ogr",
                canonical_name="ограждение",
                aliases=["OGR", "огр", "ОГР", "fence"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="OGRADA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=False,
                color=8
            ),
            
            # Vegetation codes
            CodeRule(
                code="der",
                canonical_name="дерево",
                aliases=["DER", "дер", "ДЕР", "tree"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="DEREVO", layer="BLOCKS_VEG"),
                text_layer="TEXT_VEG",
                generate_label=True,
                label_format="Д{number}",
                fallback_label="Дб/н",
                color=3
            ),
            CodeRule(
                code="kust",
                canonical_name="кустарник",
                aliases=["KUST", "куст", "КУСТ", "bush"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="KUST", layer="BLOCKS_VEG"),
                text_layer="TEXT_VEG",
                generate_label=False,
                color=3
            ),
            
            # Road/path codes
            CodeRule(
                code="dor",
                canonical_name="дорога",
                aliases=["DOR", "дор", "ДОР", "road"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="DOROGA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=False,
                color=7
            ),
            CodeRule(
                code="trop",
                canonical_name="тропа",
                aliases=["TROP", "троп", "ТРОП", "path"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TROPA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=False,
                color=8
            ),
            
            # Water features
            CodeRule(
                code="ur-vod",
                canonical_name="урез_воды",
                aliases=["urvod", "урез", "water_edge"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="UREZ_VODY", layer="BLOCKS_HYDRO"),
                text_layer="TEXT_HYDRO",
                generate_label=True,
                label_format="УВ{number}",
                fallback_label="УВб/н",
                color=5
            ),
            CodeRule(
                code="kolod",
                canonical_name="колодец",
                aliases=["KOLOD", "колод", "КОЛОД", "well"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="KOLODEC", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="Кл{number}",
                fallback_label="Клб/н",
                color=5
            ),
            
            # Terrain features
            CodeRule(
                code="otkos",
                canonical_name="откос",
                aliases=["OTKOS", "откос", "ОТКОС", "slope"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="OTKOS", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=False,
                color=7
            ),
            CodeRule(
                code="nasip",
                canonical_name="насыпь",
                aliases=["NASIP", "насип", "НАСИП", "embankment"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="NASIP", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=False,
                color=7
            ),
            
            # Boundary markers
            CodeRule(
                code="gr",
                canonical_name="граница",
                aliases=["GR", "гр", "ГР", "boundary"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="GRANICA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="Гр{number}",
                fallback_label="Грб/н",
                color=1
            ),
            CodeRule(
                code="znak",
                canonical_name="знак",
                aliases=["ZNAK", "знак", "ЗНАК", "sign"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="ZNAK", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="З{number}",
                fallback_label="Зб/н",
                color=2
            ),
            
            # Additional numbered codes for completeness (6-20)
            CodeRule(
                code="6",
                canonical_name="точка6",
                aliases=["т6", "tochka6", "t6"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=6
            ),
            CodeRule(
                code="7",
                canonical_name="точка7",
                aliases=["т7", "tochka7", "t7"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=7
            ),
            CodeRule(
                code="8",
                canonical_name="точка8",
                aliases=["т8", "tochka8", "t8"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=8
            ),
            CodeRule(
                code="9",
                canonical_name="точка9",
                aliases=["т9", "tochka9", "t9"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=9
            ),
            CodeRule(
                code="10",
                canonical_name="точка10",
                aliases=["т10", "tochka10", "t10"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=7
            ),
            
            # Additional utility codes
            CodeRule(
                code="luk",
                canonical_name="люк",
                aliases=["LUK", "люк", "ЛЮК", "hatch"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="LUK", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="Л{number}",
                fallback_label="Лб/н",
                color=7
            ),
            CodeRule(
                code="stolb",
                canonical_name="столб",
                aliases=["STOLB", "столб", "СТОЛБ", "pole", "post"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="STOLB", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="Ст{number}",
                fallback_label="Стб/н",
                color=7
            ),
            CodeRule(
                code="osvesh",
                canonical_name="освещение",
                aliases=["OSVESH", "освещ", "ОСВЕЩ", "light"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="OSVESH", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="О{number}",
                fallback_label="Об/н",
                color=7
            ),
            
            # Additional numbers (11-20)
            CodeRule(
                code="11",
                canonical_name="точка11",
                aliases=["т11", "tochka11"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=7
            ),
            CodeRule(
                code="12",
                canonical_name="точка12",
                aliases=["т12", "tochka12"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=7
            ),
            CodeRule(
                code="15",
                canonical_name="точка15",
                aliases=["т15", "tochka15"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=7
            ),
            CodeRule(
                code="20",
                canonical_name="точка20",
                aliases=["т20", "tochka20"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=7
            ),
            
            # Additional specialized codes
            CodeRule(
                code="bpl",
                canonical_name="структурная_линия",
                aliases=["BPL", "breakline"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="BREAKLINE", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=False,
                color=4
            ),
            CodeRule(
                code="cpl",
                canonical_name="осевая_линия",
                aliases=["CPL", "centerline"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="CENTERLINE", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=False,
                color=2
            ),
            CodeRule(
                code="bord",
                canonical_name="граница_участка",
                aliases=["BORD", "border"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="BORDER", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=False,
                color=1
            ),
            CodeRule(
                code="terrain",
                canonical_name="рельеф",
                aliases=["TERRAIN", "relief"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.NO_COMMENT,
                block=None,
                text_layer="TEXT",
                generate_label=False,
                color=7
            ),
            
            # Archaeological additional codes
            CodeRule(
                code="raskop",
                canonical_name="раскоп",
                aliases=["RASKOP", "раскоп", "excavation"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.BLOCK_LAYER,
                block=BlockPlacement(block_name="RASKOP", layer="BLOCKS_ARCH"),
                text_layer="BLOCKS_ARCH",
                comment_layer="BLOCKS_ARCH",
                generate_label=True,
                label_format="Р{number}",
                fallback_label="Рб/н",
                color=6
            ),
            CodeRule(
                code="nahodka",
                canonical_name="находка",
                aliases=["NAHODKA", "находка", "find"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="NAHODKA", layer="BLOCKS_ARCH"),
                text_layer="TEXT_ARCH",
                generate_label=True,
                label_format="Н{number}",
                fallback_label="Нб/н",
                color=5
            ),
            
            # More infrastructure
            CodeRule(
                code="most",
                canonical_name="мост",
                aliases=["MOST", "мост", "МОСТ", "bridge"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="MOST", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="М{number}",
                fallback_label="Мб/н",
                color=7
            ),
            CodeRule(
                code="tun",
                canonical_name="туннель",
                aliases=["TUN", "тун", "ТУН", "tunnel"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TUNNEL", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="Ту{number}",
                fallback_label="Туб/н",
                color=7
            ),
            
            # Special technical codes
            CodeRule(
                code="trig",
                canonical_name="триангуляция",
                aliases=["TRIG", "триг", "ТРИГ", "triangulation"],
                rule_type=RuleType.VK_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TRIG_PUNKT", layer="VK"),
                text_layer="VK",
                generate_label=True,
                label_format="ТР{number}",
                fallback_label="ТРб/н",
                color=1
            ),
            CodeRule(
                code="poly",
                canonical_name="полигонометрия",
                aliases=["POLY", "полиг", "ПОЛИГ", "traverse"],
                rule_type=RuleType.VK_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="POLY_PUNKT", layer="VK"),
                text_layer="VK",
                generate_label=True,
                label_format="ПП{number}",
                fallback_label="ППб/н",
                color=1
            ),
            
            # More vegetation
            CodeRule(
                code="les",
                canonical_name="лес",
                aliases=["LES", "лес", "ЛЕС", "forest"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="LES", layer="BLOCKS_VEG"),
                text_layer="TEXT_VEG",
                generate_label=False,
                color=3
            ),
            CodeRule(
                code="sad",
                canonical_name="сад",
                aliases=["SAD", "сад", "САД", "garden"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="SAD", layer="BLOCKS_VEG"),
                text_layer="TEXT_VEG",
                generate_label=False,
                color=3
            ),
            
            # Additional codes to reach 60+
            CodeRule(
                code="13",
                canonical_name="точка13",
                aliases=["т13", "tochka13"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=7
            ),
            CodeRule(
                code="14",
                canonical_name="точка14",
                aliases=["т14", "tochka14"],
                rule_type=RuleType.NUMBER_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="TOCHKA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="N{number}",
                fallback_label="Nб/н",
                color=7
            ),
            CodeRule(
                code="opn",
                canonical_name="опорная_точка",
                aliases=["OPN", "опн", "ОПН", "support"],
                rule_type=RuleType.VK_RULE,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="OPN_PUNKT", layer="VK"),
                text_layer="VK",
                generate_label=True,
                label_format="ОП{number}",
                fallback_label="ОПб/н",
                color=1
            ),
            CodeRule(
                code="plosh",
                canonical_name="площадка",
                aliases=["PLOSH", "площ", "ПЛОЩ", "platform"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="PLOSHAD", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=True,
                label_format="Пл{number}",
                fallback_label="Плб/н",
                color=7
            ),
            CodeRule(
                code="lest",
                canonical_name="лестница",
                aliases=["LEST", "лест", "ЛЕСТ", "stairs"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="LESTNICA", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=False,
                color=7
            ),
            CodeRule(
                code="parapet",
                canonical_name="парапет",
                aliases=["PARAPET", "пар", "ПАР"],
                rule_type=RuleType.STANDARD,
                comment_handling=CommentHandling.SEPARATE_LAYER,
                block=BlockPlacement(block_name="PARAPET", layer="BLOCKS"),
                text_layer="TEXT",
                generate_label=False,
                color=7
            ),
        ]
        
        for rule in rules:
            self._rules[rule.code.lower()] = rule
            for alias in rule.aliases:
                self._alias_map[alias.lower()] = rule.code.lower()
    
    def get_rule(self, code: str) -> Optional[CodeRule]:
        """
        Get rule for a survey code.
        
        Args:
            code: Survey code (case-insensitive)
            
        Returns:
            CodeRule if found, None otherwise
        """
        code_lower = code.lower()
        
        if code_lower in self._rules:
            return self._rules[code_lower]
        
        if code_lower in self._alias_map:
            canonical_code = self._alias_map[code_lower]
            return self._rules[canonical_code]
        
        return None
    
    def get_all_codes(self) -> List[str]:
        """Get list of all primary survey codes."""
        return list(self._rules.keys())
    
    def get_codes_by_rule_type(self, rule_type: RuleType) -> List[str]:
        """Get all codes matching a specific rule type."""
        return [code for code, rule in self._rules.items() 
                if rule.rule_type == rule_type]
    
    def is_known_code(self, code: str) -> bool:
        """Check if code is known in catalog."""
        return self.get_rule(code) is not None
    
    def get_catalog_statistics(self) -> Dict[str, int]:
        """Get statistics about the catalog."""
        stats = {
            'total_codes': len(self._rules),
            'total_aliases': len(self._alias_map),
            'number_rules': len(self.get_codes_by_rule_type(RuleType.NUMBER_RULE)),
            'km_rules': len(self.get_codes_by_rule_type(RuleType.KM_RULE)),
            'vk_rules': len(self.get_codes_by_rule_type(RuleType.VK_RULE)),
            'standard_rules': len(self.get_codes_by_rule_type(RuleType.STANDARD)),
        }
        return stats
