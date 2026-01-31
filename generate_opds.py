#!/usr/bin/env python3
"""
OPDS Catalog Generator for Bloomberg Daily

Generates a static OPDS 1.2 catalog from EPUBs in the books/ directory.
Designed for GitHub Pages hosting and CrossPoint e-ink reader compatibility.

Usage:
    python generate_opds.py

Output:
    opds.xml - OPDS catalog feed
    health.json - System health check endpoint

Environment Variables:
    BLOOMBERG_DEBUG - Set to '1', 'true', or 'yes' for verbose logging
    OPDS_BASE_URL - Base URL for absolute links (optional)
"""

import os
import re
import sys
import json
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

# ============================================================================
# Logging Configuration
# ============================================================================

DEBUG = os.environ.get('BLOOMBERG_DEBUG', '').lower() in ('1', 'true', 'yes')

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger('generate_opds')

if DEBUG:
    log.debug("Debug mode enabled")

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
BOOKS_DIR = SCRIPT_DIR / "books"
OPDS_OUTPUT = SCRIPT_DIR / "opds.xml"
HEALTH_OUTPUT = SCRIPT_DIR / "health.json"
BASE_URL = os.environ.get("OPDS_BASE_URL", "https://mylesmcook.github.io/bloomberg-daily/")

# ============================================================================
# Helper Functions
# ============================================================================

def get_books():
    """Get list of EPUB files sorted by date (newest first)."""
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
        log.debug(f"  - {book.name} (date: {extract_date(book)})")

    return sorted_books


def format_title(filename):
    """
    Convert filename to display title.
    Bloomberg_2026-01-31.epub -> "Daily Briefing - Jan 31"
    """
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        year, month, day = match.groups()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_name = month_names[int(month) - 1]
        return f"Daily Briefing - {month_name} {int(day)}"

    # Fallback: clean up filename
    return Path(filename).stem.replace('_', ' ')


def extract_date_from_filename(filename):
    """Extract YYYY-MM-DD date from filename."""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    return match.group(1) if match else None


# ============================================================================
# OPDS Generation
# ============================================================================

def generate_entry(book_path):
    """Generate OPDS entry XML for a single book."""
    log.debug(f"Generating entry for: {book_path.name}")

    try:
        stat = book_path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        size = stat.st_size
        book_id = hashlib.md5(book_path.name.encode()).hexdigest()
        title = format_title(book_path.name)

        # URL for the book (absolute URL for maximum OPDS reader compatibility)
        book_url = f"{BASE_URL}books/{book_path.name}"

        # XML escape all dynamic content for safety
        safe_title = xml_escape(title)
        safe_url = xml_escape(book_url)

        log.debug(f"  Title: {safe_title}, Size: {size}, ID: {book_id[:8]}...")

        return f'''
    <entry>
        <title>{safe_title}</title>
        <id>urn:uuid:{book_id}</id>
        <updated>{modified}</updated>
        <author>
            <name>Bloomberg News</name>
        </author>
        <dc:publisher>Bloomberg L.P.</dc:publisher>
        <category term="news" label="News"/>
        <category term="technology" label="Technology"/>
        <category term="business" label="Business"/>
        <summary>AI, Technology, Industries, and Latest news from Bloomberg</summary>
        <content type="text">AI · Technology · Industries · Latest</content>
        <link href="{safe_url}" rel="http://opds-spec.org/acquisition" type="application/epub+zip" length="{size}"/>
        <link href="{safe_url}" rel="http://opds-spec.org/acquisition/open-access" type="application/epub+zip"/>
    </entry>'''

    except Exception as e:
        log.error(f"Failed to generate entry for {book_path}")
        log.error(f"  File exists: {book_path.exists()}")
        log.error(f"  Exception: {e}")
        raise


def generate_catalog():
    """Generate complete OPDS catalog XML."""
    log.info("Generating OPDS catalog...")

    books = get_books()
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    entries = []
    for book in books:
        try:
            entry = generate_entry(book)
            entries.append(entry)
        except Exception as e:
            log.error(f"Skipping {book.name} due to error: {e}")

    # Count for subtitle
    book_count = len(entries)
    if book_count == 0:
        subtitle = "No issues available"
    elif book_count == 1:
        subtitle = "1 issue available"
    else:
        subtitle = f"{book_count} issues available (rolling weekly archive)"

    log.info(f"Generated {book_count} entries")

    catalog = f'''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:dc="http://purl.org/dc/terms/"
      xmlns:opds="http://opds-spec.org/2010/catalog">

    <id>urn:uuid:bloomberg-daily-opds-feed</id>
    <title>Bloomberg Daily Briefing</title>
    <subtitle>{xml_escape(subtitle)}</subtitle>
    <icon>https://assets.bwbx.io/s3/javelin/public/hub/images/favicon-black-63fe5249d3.png</icon>
    <updated>{now}</updated>
    <author>
        <name>Bloomberg News Pipeline</name>
        <uri>https://github.com/MylesMCook/bloomberg-daily</uri>
    </author>

    <link href="{BASE_URL}opds.xml" rel="self" type="application/atom+xml;profile=opds-catalog;kind=acquisition"/>
    <link href="{BASE_URL}opds.xml" rel="start" type="application/atom+xml;profile=opds-catalog;kind=acquisition"/>
    {''.join(entries)}
</feed>'''

    return catalog


# ============================================================================
# Health Check Generation
# ============================================================================

def generate_health_check():
    """Generate health.json for quick system status verification."""
    log.info("Generating health check...")

    books = get_books()
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    total_size = sum(b.stat().st_size for b in books) if books else 0
    dates = [extract_date_from_filename(b.name) for b in books]
    dates = [d for d in dates if d]  # Filter out None

    health = {
        "status": "ok" if books else "empty",
        "last_update": now,
        "book_count": len(books),
        "oldest_book": min(dates) if dates else None,
        "newest_book": max(dates) if dates else None,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / 1024 / 1024, 2),
        "opds_url": f"{BASE_URL}opds.xml",
        "books": [
            {
                "filename": b.name,
                "date": extract_date_from_filename(b.name),
                "size_bytes": b.stat().st_size,
                "title": format_title(b.name)
            }
            for b in books
        ]
    }

    log.info(f"Health status: {health['status']}, {health['book_count']} books, {health['total_size_mb']} MB")

    return health


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point."""
    log.info("=" * 60)
    log.info("Bloomberg OPDS Generator")
    log.info("=" * 60)

    try:
        # Generate OPDS catalog
        log.info(f"Books directory: {BOOKS_DIR}")
        books = get_books()
        log.info(f"Found {len(books)} EPUB(s)")

        for book in books:
            size_mb = book.stat().st_size / 1024 / 1024
            log.info(f"  - {book.name} ({size_mb:.1f} MB)")

        catalog = generate_catalog()

        # Write OPDS catalog
        OPDS_OUTPUT.write_text(catalog, encoding='utf-8')
        log.info(f"OPDS catalog written: {OPDS_OUTPUT}")
        log.info(f"Catalog size: {len(catalog)} bytes")

        # Generate and write health check
        health = generate_health_check()
        HEALTH_OUTPUT.write_text(json.dumps(health, indent=2), encoding='utf-8')
        log.info(f"Health check written: {HEALTH_OUTPUT}")

        log.info("=" * 60)
        log.info("Generation complete!")
        log.info("=" * 60)

    except Exception as e:
        log.error("=" * 60)
        log.error("GENERATION FAILED")
        log.error("=" * 60)
        log.error(f"Exception: {e}")
        log.error(f"Books directory exists: {BOOKS_DIR.exists()}")
        log.error(f"Working directory: {Path.cwd()}")
        raise


if __name__ == "__main__":
    main()
