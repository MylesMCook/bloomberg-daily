"""
Configuration Schema for News-to-EPUB Pipeline

Pydantic models for validating sources.yaml configuration.
Supports multiple source types: calibre_recipe, gutenberg, custom.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class SourceType(str, Enum):
    """Supported source types."""
    CALIBRE_RECIPE = "calibre_recipe"
    GUTENBERG = "gutenberg"
    CUSTOM = "custom"


class ScheduleMode(str, Enum):
    """Schedule modes for sources."""
    SCHEDULED = "scheduled"      # Runs on cron schedule
    ON_DEMAND = "on_demand"      # Manual trigger only


class RateLimitConfig(BaseModel):
    """Rate limiting configuration for respectful scraping."""
    requests_per_second: float = Field(default=1.0, ge=0.1, le=10.0)
    cache_hours: int = Field(default=24, ge=1, le=168)
    
    
class DeviceProfile(BaseModel):
    """Device-specific output configuration."""
    css_theme: str = Field(default="default")
    skip_pages: list[int] = Field(default_factory=list)
    font_size_adjust: float = Field(default=1.0, ge=0.5, le=2.0)
    strip_images: bool = Field(default=False)
    grayscale_images: bool = Field(default=True)


class SourceConfig(BaseModel):
    """Configuration for a single news source."""
    name: str = Field(..., min_length=1, max_length=100)
    type: SourceType
    enabled: bool = Field(default=True)
    
    # Scheduling
    mode: ScheduleMode = Field(default=ScheduleMode.SCHEDULED)
    schedule: Optional[str] = Field(default=None, description="Cron expression")
    
    # Calibre recipe sources
    recipe: Optional[str] = Field(default=None, description="Recipe filename")
    sections: list[str] = Field(default_factory=list)
    
    # Gutenberg sources
    search_query: Optional[str] = Field(default=None)
    
    # Common settings
    retention_days: int = Field(default=7, ge=1, le=365)
    rate_limit: Optional[RateLimitConfig] = Field(default=None)
    
    # Device profiles
    device_profiles: dict[str, DeviceProfile] = Field(default_factory=dict)
    
    # Custom metadata
    author_override: Optional[str] = Field(default=None)
    publisher_override: Optional[str] = Field(default=None)
    
    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v: Optional[str], info) -> Optional[str]:
        """Validate cron expression format."""
        if v is None:
            return v
        parts = v.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {v}")
        return v
    
    @field_validator("recipe")
    @classmethod
    def validate_recipe(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure recipe is provided for calibre_recipe type."""
        # Note: Full validation happens at the Config level
        return v


class Config(BaseModel):
    """Root configuration model."""
    version: str = Field(default="1.0")
    base_url: str = Field(default="https://mylesmcook.github.io/bloomberg-daily/")
    sources: dict[str, SourceConfig] = Field(default_factory=dict)
    
    # Global settings
    default_retention_days: int = Field(default=7, ge=1, le=365)
    default_rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    
    @field_validator("sources")
    @classmethod
    def validate_sources(cls, v: dict[str, SourceConfig]) -> dict[str, SourceConfig]:
        """Validate all sources have required fields for their type."""
        for source_id, source in v.items():
            if source.type == SourceType.CALIBRE_RECIPE and not source.recipe:
                raise ValueError(f"Source '{source_id}' is calibre_recipe type but has no recipe")
            if source.mode == ScheduleMode.SCHEDULED and not source.schedule:
                raise ValueError(f"Source '{source_id}' is scheduled but has no cron schedule")
        return v
    
    def get_enabled_sources(self) -> dict[str, SourceConfig]:
        """Get only enabled sources."""
        return {k: v for k, v in self.sources.items() if v.enabled}
    
    def get_scheduled_sources(self) -> dict[str, SourceConfig]:
        """Get sources that run on a schedule."""
        return {
            k: v for k, v in self.sources.items() 
            if v.enabled and v.mode == ScheduleMode.SCHEDULED
        }
    
    def get_on_demand_sources(self) -> dict[str, SourceConfig]:
        """Get sources that are triggered manually."""
        return {
            k: v for k, v in self.sources.items() 
            if v.enabled and v.mode == ScheduleMode.ON_DEMAND
        }
