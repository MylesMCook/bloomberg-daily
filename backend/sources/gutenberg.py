"""
Project Gutenberg Source Plugin

Fetches free ebooks from Project Gutenberg with respectful rate limiting.
Supports search by title, author, and subject.

API: https://gutendex.com/ (unofficial API for Gutenberg)
"""

import time
import logging
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
import urllib.request
import urllib.parse
import json

from backend.config import SourceConfig
from .base import BaseSource, FetchResult, BookMetadata

log = logging.getLogger(__name__)

# Gutendex API endpoint (unofficial but reliable)
GUTENDEX_API = "https://gutendex.com/books"

# Cache for search results
_search_cache: dict[str, tuple[float, list[BookMetadata]]] = {}


@dataclass
class GutenbergBook(BookMetadata):
    """Extended metadata for Gutenberg books."""
    gutenberg_id: int = 0
    download_count: int = 0
    formats: dict[str, str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.formats is None:
            self.formats = {}
    
    def get_epub_url(self) -> Optional[str]:
        """Get EPUB download URL, preferring no-images version."""
        # Prefer EPUB without images (smaller, better for e-ink)
        for fmt in ["application/epub+zip", "application/epub"]:
            if fmt in self.formats:
                return self.formats[fmt]
        return None


class GutenbergSource(BaseSource):
    """
    Project Gutenberg source plugin.
    
    Provides on-demand access to free public domain books.
    Uses the Gutendex API for search and metadata.
    """
    
    def __init__(self, config: SourceConfig, output_dir: Path):
        super().__init__(config, output_dir)
        self._last_request_time = 0.0
        
        # Rate limiting from config
        rate_limit = config.rate_limit
        self._min_request_interval = 1.0 / rate_limit.requests_per_second if rate_limit else 1.0
        self._cache_hours = rate_limit.cache_hours if rate_limit else 24
    
    @property
    def source_type(self) -> str:
        return "gutenberg"
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            sleep_time = self._min_request_interval - elapsed
            log.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def _make_request(self, url: str) -> dict:
        """Make an HTTP request with rate limiting and error handling."""
        self._rate_limit()
        
        log.debug(f"Requesting: {url}")
        
        headers = {
            "User-Agent": "BloombergDaily/1.0 (e-ink reader news aggregator; contact: github.com/MylesMCook/bloomberg-daily)"
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            log.error(f"HTTP error {e.code}: {e.reason}")
            raise
        except urllib.error.URLError as e:
            log.error(f"URL error: {e.reason}")
            raise
    
    def search(
        self, 
        query: str = "",
        author: str = "",
        title: str = "",
        topic: str = "",
        language: str = "en",
        page: int = 1
    ) -> list[GutenbergBook]:
        """
        Search Project Gutenberg catalog.
        
        Args:
            query: General search query
            author: Author name filter
            title: Title filter
            topic: Subject/topic filter
            language: Language code (default: en)
            page: Result page number
            
        Returns:
            List of GutenbergBook metadata objects.
        """
        # Build query parameters
        params = {"page": page}
        if query:
            params["search"] = query
        if author:
            params["author"] = author
        if title:
            params["title"] = title
        if topic:
            params["topic"] = topic
        if language:
            params["languages"] = language
        
        # Check cache
        cache_key = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        if cache_key in _search_cache:
            cached_time, cached_results = _search_cache[cache_key]
            cache_age_hours = (time.time() - cached_time) / 3600
            if cache_age_hours < self._cache_hours:
                log.debug(f"Using cached search results (age: {cache_age_hours:.1f}h)")
                return cached_results
        
        # Make API request
        url = f"{GUTENDEX_API}?{urllib.parse.urlencode(params)}"
        data = self._make_request(url)
        
        # Parse results
        books = []
        for item in data.get("results", []):
            book = self._parse_book(item)
            if book:
                books.append(book)
        
        # Cache results
        _search_cache[cache_key] = (time.time(), books)
        
        log.info(f"Found {len(books)} books (total: {data.get('count', 0)})")
        return books
    
    def _parse_book(self, item: dict) -> Optional[GutenbergBook]:
        """Parse API response item into GutenbergBook."""
        try:
            # Get first author
            authors = item.get("authors", [])
            author_name = authors[0]["name"] if authors else "Unknown"
            
            # Get subjects
            subjects = [s for s in item.get("subjects", [])]
            
            # Get cover image
            formats = item.get("formats", {})
            cover_url = formats.get("image/jpeg")
            
            return GutenbergBook(
                gutenberg_id=item["id"],
                title=item["title"],
                author=author_name,
                identifier=f"gutenberg:{item['id']}",
                language=item.get("languages", ["en"])[0],
                subjects=subjects,
                cover_url=cover_url,
                download_count=item.get("download_count", 0),
                formats=formats,
            )
        except (KeyError, IndexError) as e:
            log.warning(f"Failed to parse book: {e}")
            return None
    
    def get_book(self, gutenberg_id: int) -> Optional[GutenbergBook]:
        """
        Get metadata for a specific book by Gutenberg ID.
        
        Args:
            gutenberg_id: Project Gutenberg book ID
            
        Returns:
            GutenbergBook metadata or None if not found.
        """
        url = f"{GUTENDEX_API}/{gutenberg_id}"
        
        try:
            data = self._make_request(url)
            return self._parse_book(data)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                log.warning(f"Book not found: {gutenberg_id}")
                return None
            raise
    
    def download_book(self, book: GutenbergBook) -> FetchResult:
        """
        Download EPUB for a specific book.
        
        Args:
            book: GutenbergBook metadata with download URLs.
            
        Returns:
            FetchResult with success status and EPUB path.
        """
        start_time = time.time()
        
        epub_url = book.get_epub_url()
        if not epub_url:
            return FetchResult(
                success=False,
                error_message=f"No EPUB format available for: {book.title}"
            )
        
        # Generate filename
        safe_title = "".join(c for c in book.title if c.isalnum() or c in " -_")[:50]
        filename = f"Gutenberg_{book.gutenberg_id}_{safe_title}.epub"
        output_path = self.output_dir / filename
        
        # Check if already downloaded
        if output_path.exists():
            log.info(f"Book already downloaded: {filename}")
            return FetchResult(
                success=True,
                epub_path=output_path,
                title=book.title,
                author=book.author,
            )
        
        # Download EPUB
        log.info(f"Downloading: {book.title} ({epub_url})")
        self._rate_limit()
        
        try:
            headers = {
                "User-Agent": "BloombergDaily/1.0 (e-ink reader news aggregator)"
            }
            req = urllib.request.Request(epub_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read()
            
            # Write to file
            output_path.write_bytes(content)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            log.info(f"Downloaded: {filename} ({len(content):,} bytes)")
            
            return FetchResult(
                success=True,
                epub_path=output_path,
                title=book.title,
                author=book.author,
                fetch_duration_ms=duration_ms,
            )
            
        except Exception as e:
            log.error(f"Download failed: {e}")
            return FetchResult(
                success=False,
                error_message=str(e),
                title=book.title,
                author=book.author,
            )
    
    def fetch(self) -> FetchResult:
        """
        Default fetch - not applicable for on-demand source.
        
        Use search() and download_book() instead.
        """
        return FetchResult(
            success=False,
            error_message="Gutenberg is an on-demand source. Use search() and download_book() instead."
        )
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate Gutenberg source configuration."""
        # Test API connectivity
        try:
            self._make_request(f"{GUTENDEX_API}?page=1")
            return True, None
        except Exception as e:
            return False, f"Cannot connect to Gutenberg API: {e}"
