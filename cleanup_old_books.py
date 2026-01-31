#!/usr/bin/env python3
"""
Cleanup Script for Bloomberg Daily Archive

Maintains a rolling 7-day archive by removing old EPUBs.
Designed to run as part of the GitHub Actions workflow.

Usage:
    python cleanup_old_books.py [--keep N]

Arguments:
    --keep N    Number of recent EPUBs to keep (default: 7)

Environment Variables:
    BLOOMBERG_DEBUG - Set to '1', 'true', or 'yes' for verbose logging
"""

import os
import sys
import argparse
import re
import logging
from pathlib import Path

# ============================================================================
# Logging Configuration
# ============================================================================

DEBUG = os.environ.get('BLOOMBERG_DEBUG', '').lower() in ('1', 'true', 'yes')

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger('cleanup')

if DEBUG:
    log.debug("Debug mode enabled")

# ============================================================================
# Configuration
# ============================================================================

BOOKS_DIR = Path(__file__).parent / "books"

# ============================================================================
# Functions
# ============================================================================

def get_books_by_date():
    """Get list of EPUB files sorted by date extracted from filename."""
    log.debug(f"Scanning for EPUBs in: {BOOKS_DIR}")

    if not BOOKS_DIR.exists():
        log.warning(f"Books directory does not exist: {BOOKS_DIR}")
        return []

    epubs = list(BOOKS_DIR.glob("*.epub"))
    log.debug(f"Found {len(epubs)} EPUB files")

    def extract_date(path):
        match = re.search(r'(\d{4}-\d{2}-\d{2})', path.name)
        if match:
            return match.group(1)
        return "0000-00-00"

    sorted_books = sorted(epubs, key=extract_date, reverse=True)

    for book in sorted_books:
        log.debug(f"  - {book.name} (date: {extract_date(book)}, size: {book.stat().st_size:,} bytes)")

    return sorted_books


def cleanup(keep_count=7):
    """Remove old EPUBs, keeping only the most recent ones."""
    log.info("=" * 60)
    log.info("Bloomberg Archive Cleanup")
    log.info("=" * 60)

    books = get_books_by_date()

    log.info(f"Found {len(books)} EPUB(s) in {BOOKS_DIR}")
    log.info(f"Keep policy: {keep_count} most recent")

    if len(books) <= keep_count:
        log.info("No cleanup needed - within retention limit")
        return []

    to_remove = books[keep_count:]
    removed = []

    log.info(f"Removing {len(to_remove)} old EPUB(s):")

    for old_book in to_remove:
        try:
            size = old_book.stat().st_size
            log.info(f"  Removing: {old_book.name} ({size:,} bytes)")
            old_book.unlink()
            removed.append(old_book.name)
        except Exception as e:
            log.error(f"  Failed to remove {old_book.name}: {e}")

    log.info("=" * 60)
    log.info(f"Cleanup complete: removed {len(removed)} file(s)")
    log.info("=" * 60)

    return removed


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Clean up old Bloomberg EPUBs")
    parser.add_argument("--keep", type=int, default=7,
                       help="Number of EPUBs to keep (default: 7)")
    args = parser.parse_args()

    try:
        cleanup(args.keep)
    except Exception as e:
        log.error(f"FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
