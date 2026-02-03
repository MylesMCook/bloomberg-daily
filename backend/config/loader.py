"""
Configuration Loader

Loads and validates sources.yaml configuration file.
Provides singleton access to configuration throughout the application.
"""

import os
import logging
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from .schema import Config, SourceConfig

log = logging.getLogger(__name__)

# Configuration singleton
_config: Optional[Config] = None


def get_config_path() -> Path:
    """Get path to sources.yaml configuration file."""
    # Check environment variable first
    env_path = os.environ.get("CONFIG_PATH")
    if env_path:
        return Path(env_path)
    
    # Default locations to check
    locations = [
        Path(__file__).parent.parent.parent / "config" / "sources.yaml",
        Path.cwd() / "config" / "sources.yaml",
        Path.cwd() / "sources.yaml",
    ]
    
    for path in locations:
        if path.exists():
            return path
    
    # Return default location even if it doesn't exist
    return locations[0]


def load_config(path: Optional[Path] = None, reload: bool = False) -> Config:
    """
    Load and validate configuration from YAML file.
    
    Args:
        path: Optional path to config file. Uses default if not provided.
        reload: Force reload even if already loaded.
        
    Returns:
        Validated Config object.
        
    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValidationError: If config is invalid.
    """
    global _config
    
    if _config is not None and not reload:
        return _config
    
    config_path = path or get_config_path()
    
    log.info(f"Loading configuration from: {config_path}")
    
    if not config_path.exists():
        log.warning(f"Config file not found: {config_path}")
        log.info("Using default configuration")
        _config = Config()
        return _config
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)
        
        if raw_config is None:
            log.warning("Config file is empty, using defaults")
            _config = Config()
            return _config
        
        _config = Config.model_validate(raw_config)
        
        log.info(f"Loaded {len(_config.sources)} sources")
        for source_id, source in _config.sources.items():
            status = "enabled" if source.enabled else "disabled"
            log.debug(f"  - {source_id}: {source.name} ({source.type.value}) [{status}]")
        
        return _config
        
    except yaml.YAMLError as e:
        log.error(f"Failed to parse YAML: {e}")
        raise
    except ValidationError as e:
        log.error(f"Configuration validation failed:")
        for error in e.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            log.error(f"  {loc}: {error['msg']}")
        raise


def get_config() -> Config:
    """
    Get the current configuration (loads if not already loaded).
    
    Returns:
        Config object.
    """
    if _config is None:
        return load_config()
    return _config


def get_source(source_id: str) -> Optional[SourceConfig]:
    """
    Get a specific source by ID.
    
    Args:
        source_id: Source identifier (key in sources dict).
        
    Returns:
        SourceConfig if found, None otherwise.
    """
    config = get_config()
    return config.sources.get(source_id)


def save_config(config: Config, path: Optional[Path] = None) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Config object to save.
        path: Optional path. Uses default if not provided.
    """
    config_path = path or get_config_path()
    
    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to dict and save
    config_dict = config.model_dump(exclude_none=True)
    
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
    
    log.info(f"Configuration saved to: {config_path}")
    
    # Update singleton
    global _config
    _config = config
