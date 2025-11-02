"""Bot-specific data models for state management."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class FileUploadInfo:
    """Information about uploaded file."""
    file_path: Path
    original_filename: str
    file_size: int
    encoding: Optional[str] = None
    delimiter: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'file_path': str(self.file_path),
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'encoding': self.encoding,
            'delimiter': self.delimiter
        }


@dataclass
class ColumnMapping:
    """Column mapping configuration for parsing."""
    name_col: Optional[int] = None
    x_col: int = 0
    y_col: int = 1
    z_col: int = 2
    code_col: Optional[int] = 3
    comment_col: Optional[int] = 4
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name_col': self.name_col,
            'x_col': self.x_col,
            'y_col': self.y_col,
            'z_col': self.z_col,
            'code_col': self.code_col,
            'comment_col': self.comment_col
        }


@dataclass
class ParsedData:
    """Parsed data from uploaded file."""
    points: List[Dict[str, Any]]
    total_rows: int
    valid_rows: int
    invalid_rows: int
    anomalies: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_rows': self.total_rows,
            'valid_rows': self.valid_rows,
            'invalid_rows': self.invalid_rows,
            'anomalies': self.anomalies,
            'warnings': self.warnings
        }


@dataclass
class BotSessionData:
    """Session data stored in context.user_data."""
    file_info: Optional[FileUploadInfo] = None
    column_mapping: ColumnMapping = field(default_factory=ColumnMapping)
    parsed_data: Optional[ParsedData] = None
    use_template: bool = False
    scale: float = 1.0
    tin_enabled: bool = True
    densification_enabled: bool = False
    processing_extras: Dict[str, Any] = field(default_factory=dict)
    
    def reset(self):
        """Reset session data."""
        self.file_info = None
        self.column_mapping = ColumnMapping()
        self.parsed_data = None
        self.use_template = False
        self.scale = 1.0
        self.tin_enabled = True
        self.densification_enabled = False
        self.processing_extras = {}
