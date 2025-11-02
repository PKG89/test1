"""Configuration management for CAD-P bot."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    SRC_DIR = BASE_DIR / "src"
    
    # Bot configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "logs/bot.log")
    
    # File storage paths
    TEMP_DIR: Path = BASE_DIR / os.getenv("TEMP_DIR", "temp/uploads")
    OUTPUT_DIR: Path = BASE_DIR / os.getenv("OUTPUT_DIR", "output")
    TEMPLATES_DIR: Path = BASE_DIR / os.getenv("TEMPLATES_DIR", "templates")
    DATA_DIR: Path = BASE_DIR / os.getenv("DATA_DIR", "data")
    
    # Processing configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    MAX_POINTS: int = int(os.getenv("MAX_POINTS", "1000000"))
    DEFAULT_GRID_SPACING: float = float(os.getenv("DEFAULT_GRID_SPACING", "5.0"))
    
    # Feature toggles
    ENABLE_DENSIFICATION: bool = os.getenv("ENABLE_DENSIFICATION", "true").lower() == "true"
    ENABLE_TIN: bool = os.getenv("ENABLE_TIN", "true").lower() == "true"
    ENABLE_CODE_CATALOG: bool = os.getenv("ENABLE_CODE_CATALOG", "true").lower() == "true"
    ENABLE_FILE_VALIDATION: bool = os.getenv("ENABLE_FILE_VALIDATION", "true").lower() == "true"
    ENABLE_AUTO_ENCODING_DETECTION: bool = os.getenv("ENABLE_AUTO_ENCODING_DETECTION", "true").lower() == "true"
    
    # Performance settings
    WORKER_THREADS: int = int(os.getenv("WORKER_THREADS", "4"))
    PROCESSING_TIMEOUT_SECONDS: int = int(os.getenv("PROCESSING_TIMEOUT_SECONDS", "300"))
    
    # Development settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    DEVELOPMENT_MODE: bool = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
    
    @classmethod
    def ensure_directories(cls):
        """Create required directories if they don't exist."""
        directories = [
            cls.TEMP_DIR,
            cls.OUTPUT_DIR,
            cls.TEMPLATES_DIR,
            cls.DATA_DIR,
        ]
        
        # Create logs directory if LOG_FILE is set
        if cls.LOG_FILE:
            log_dir = Path(cls.LOG_FILE).parent
            if not log_dir.is_absolute():
                log_dir = cls.BASE_DIR / log_dir
            directories.append(log_dir)
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN or TELEGRAM_BOT_TOKEN environment variable is required")
        
        if cls.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be greater than 0")
        
        if cls.MAX_POINTS <= 0:
            errors.append("MAX_POINTS must be greater than 0")
        
        if cls.DEFAULT_GRID_SPACING <= 0:
            errors.append("DEFAULT_GRID_SPACING must be greater than 0")
        
        return errors


# Global config instance
config = Config()
