"""
Configuration module for the news-to-EPUB pipeline.
"""

from .schema import (
    Config,
    SourceConfig,
    SourceType,
    ScheduleMode,
    RateLimitConfig,
    DeviceProfile,
)
from .loader import (
    load_config,
    get_config,
    get_source,
    save_config,
    get_config_path,
)

__all__ = [
    # Schema
    "Config",
    "SourceConfig",
    "SourceType",
    "ScheduleMode",
    "RateLimitConfig",
    "DeviceProfile",
    # Loader
    "load_config",
    "get_config",
    "get_source",
    "save_config",
    "get_config_path",
]
