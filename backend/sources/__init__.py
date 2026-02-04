"""
Source plugins for the news-to-EPUB pipeline.

Each source plugin handles fetching content from a specific
external source and producing EPUB files.
"""

from .base import BaseSource, FetchResult, BookMetadata
from .gutenberg import GutenbergSource, GutenbergBook

__all__ = [
    "BaseSource",
    "FetchResult", 
    "BookMetadata",
    "GutenbergSource",
    "GutenbergBook",
]
