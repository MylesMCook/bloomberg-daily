#!/usr/bin/env python3
"""
Cleanup Script for Bloomberg Daily Archive

Maintains a rolling 7-day archive by removing old EPUBs.
Designed to run as part of the GitHub Actions workflow.

Usage:
    python cleanup_old_books.py [--keep N]

Arguments:
    --keep N    Number of recent EPUBs to keep (default: 7)
"""

import argparse
import re
from pathlib import Path


BOOKS_DIR = Path(__file__).parent / "books"


def get_books_by_date():
    """Get list of EPUB files sorted by date extracted from filename."""
    if not BOOKS_DIR.exists():
        return []

    epubs = list(BOOKS_DIR.glob("*.epub"))

    def extract_date(path):
        match = re.search(r'(\d{4}-\d{2}-\d{2})', path.name)
        if match:
            return match.group(1)
        return "0000-00-00"

    return sorted(epubs, key=extract_date, reverse=True)


def cleanup(keep_count=7):
    """Remove old EPUBs, keeping only the most recent ones."""
    books = get_books_by_date()

    print(f"Found {len(books)} EPUB(s) in {BOOKS_DIR}")
    print(f"Keeping {keep_count} most recent")

    if len(books) <= keep_count:
        print("No cleanup needed")
        return []

    to_remove = books[keep_count:]
    removed = []

    for old_book in to_remove:
        print(f"Removing: {old_book.name}")
        old_book.unlink()
        removed.append(old_book.name)

    print(f"\nRemoved {len(removed)} old EPUB(s)")
    return removed


def main():
    parser = argparse.ArgumentParser(description="Clean up old Bloomberg EPUBs")
    parser.add_argument("--keep", type=int, default=7,
                       help="Number of EPUBs to keep (default: 7)")
    args = parser.parse_args()

    cleanup(args.keep)


if __name__ == "__main__":
    main()
