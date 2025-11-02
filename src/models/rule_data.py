"""Data models for rule engine and code catalog."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class RuleType(Enum):
    """Type of rule for code processing."""
    NUMBER_RULE = "№-rule"
    KM_RULE = "km-rule"
    VK_RULE = "VK-rule"
    COMMENT_BLOCK = "comment-block"
    STANDARD = "standard"


class CommentHandling(Enum):
    """Strategy for handling comments."""
    SEPARATE_LAYER = "separate"
    BLOCK_LAYER = "block"
    NO_COMMENT = "none"
    SPECIAL = "special"


@dataclass
class LayerDefinition:
    """Definition of a layer with color and properties."""
    name: str
    color: int = 7
    linetype: str = "Continuous"
    lineweight: int = 25


@dataclass
class TextPlacement:
    """Text placement configuration."""
    layer: str
    height: float = 2.5
    color: Optional[int] = None
    style: str = "Standard"
    offset_x: float = 0.0
    offset_y: float = 0.0
    bold: bool = False
    rotation: float = 0.0


@dataclass
class BlockPlacement:
    """Block placement configuration."""
    block_name: str
    layer: str
    scale: float = 1.0
    rotation: float = 0.0
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeRule:
    """Rule definition for a survey code."""
    code: str
    canonical_name: str
    aliases: List[str] = field(default_factory=list)
    rule_type: RuleType = RuleType.STANDARD
    comment_handling: CommentHandling = CommentHandling.SEPARATE_LAYER
    block: Optional[BlockPlacement] = None
    text_layer: str = "TEXT"
    comment_layer: str = "TEXT"
    point_layer: str = "POINTS"
    generate_label: bool = False
    label_format: str = "{code}{number}"
    fallback_label: str = "Nб/н"
    color: int = 7
    special_behavior: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlacementInstruction:
    """Complete placement instruction for a survey point."""
    code: str
    canonical_code: str
    x: float
    y: float
    z: float
    block: Optional[BlockPlacement] = None
    texts: List[TextPlacement] = field(default_factory=list)
    point_marker: Optional[Dict[str, Any]] = None
    labels: List[str] = field(default_factory=list)
    comment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_unknown: bool = False


@dataclass
class RuleEngineResult:
    """Result from rule engine processing."""
    instructions: List[PlacementInstruction]
    statistics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
