"""
Backend package for the news-to-EPUB pipeline.

This package contains:
- config: Configuration schema and loader
- sources: Source plugins (Bloomberg, Gutenberg, etc.)
- processors: EPUB post-processing modules
- generators: OPDS feed generation
- utils: Shared utilities (rate limiting, caching, etc.)
"""

__version__ = "0.1.0"
