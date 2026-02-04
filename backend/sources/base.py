"""
Base Source Plugin Interface

All source plugins must inherit from BaseSource and implement
the required abstract methods.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from backend.config import SourceConfig


@dataclass
class FetchResult:
    """Result of a source fetch operation."""
    success: bool
    epub_path: Optional[Path] = None
    title: str = ""
    author: str = ""
    error_message: Optional[str] = None
    fetch_duration_ms: int = 0
    article_count: int = 0
    
    @property
    def size_bytes(self) -> int:
        """Get file size if EPUB exists."""
        if self.epub_path and self.epub_path.exists():
            return self.epub_path.stat().st_size
        return 0


@dataclass 
class BookMetadata:
    """Metadata for a book/publication."""
    title: str
    author: str
    identifier: str  # ISBN, Gutenberg ID, or generated UUID
    language: str = "en"
    publisher: Optional[str] = None
    published_date: Optional[datetime] = None
    description: Optional[str] = None
    subjects: list[str] = None
    cover_url: Optional[str] = None
    download_url: Optional[str] = None
    
    def __post_init__(self):
        if self.subjects is None:
            self.subjects = []


class BaseSource(ABC):
    """
    Abstract base class for all source plugins.
    
    Source plugins are responsible for fetching content from external
    sources and producing EPUB files.
    """
    
    def __init__(self, config: SourceConfig, output_dir: Path):
        """
        Initialize the source plugin.
        
        Args:
            config: Source configuration from sources.yaml
            output_dir: Directory to write output EPUBs
        """
        self.config = config
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    @abstractmethod
    def source_type(self) -> str:
        """Return the source type identifier."""
        pass
    
    @abstractmethod
    def fetch(self) -> FetchResult:
        """
        Fetch content and produce an EPUB.
        
        For scheduled sources, this fetches the latest content.
        For on-demand sources, this may need additional parameters.
        
        Returns:
            FetchResult with success status and EPUB path.
        """
        pass
    
    @abstractmethod
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate that the source is properly configured.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        pass
    
    def get_output_filename(self, date: Optional[datetime] = None) -> str:
        """
        Generate output filename for the EPUB.
        
        Args:
            date: Date for the filename. Defaults to today.
            
        Returns:
            Filename like "Bloomberg_2026-01-15.epub"
        """
        if date is None:
            date = datetime.now()
        
        # Clean source name for filename
        safe_name = self.config.name.replace(" ", "_").replace("/", "-")
        return f"{safe_name}_{date.strftime('%Y-%m-%d')}.epub"
    
    def should_skip(self) -> tuple[bool, Optional[str]]:
        """
        Check if this fetch should be skipped.
        
        Used to avoid duplicate fetches if today's file already exists.
        
        Returns:
            Tuple of (should_skip, reason).
        """
        expected_file = self.output_dir / self.get_output_filename()
        if expected_file.exists():
            return True, f"File already exists: {expected_file.name}"
        return False, None
