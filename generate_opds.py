#!/usr/bin/env python3
"""
OPDS Catalog Generator for Bloomberg Daily

Generates a static OPDS 1.2 catalog from EPUBs in the books/ directory.
Designed for GitHub Pages hosting and CrossPoint e-ink reader compatibility.

Usage:
    python generate_opds.py

Output:
    opds.xml - OPDS catalog feed
"""

import os
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path


# Configuration
BOOKS_DIR = Path(__file__).parent / "books"
OUTPUT_FILE = Path(__file__).parent / "opds.xml"
BASE_URL = os.environ.get("OPDS_BASE_URL", "")  # Set in GitHub Actions


def get_books():
    """Get list of EPUB files sorted by date (newest first)."""
    if not BOOKS_DIR.exists():
        return []

    epubs = list(BOOKS_DIR.glob("*.epub"))

    # Sort by date extracted from filename (Bloomberg_YYYY-MM-DD.epub)
    def extract_date(path):
        match = re.search(r'(\d{4}-\d{2}-\d{2})', path.name)
        if match:
            return match.group(1)
        return "0000-00-00"

    return sorted(epubs, key=extract_date, reverse=True)


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


def generate_entry(book_path):
    """Generate OPDS entry XML for a single book."""
    stat = book_path.stat()
    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%dT%H:%M:%SZ')
    size = stat.st_size
    book_id = hashlib.md5(book_path.name.encode()).hexdigest()
    title = format_title(book_path.name)

    # URL for the book (relative path works for GitHub Pages)
    book_url = f"books/{book_path.name}"

    return f'''
    <entry>
        <title>{title}</title>
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
        <link href="{book_url}" rel="http://opds-spec.org/acquisition" type="application/epub+zip" length="{size}"/>
        <link href="{book_url}" rel="http://opds-spec.org/acquisition/open-access" type="application/epub+zip"/>
    </entry>'''


def generate_catalog():
    """Generate complete OPDS catalog XML."""
    books = get_books()
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    entries = [generate_entry(book) for book in books]

    # Count for subtitle
    book_count = len(books)
    if book_count == 0:
        subtitle = "No issues available"
    elif book_count == 1:
        subtitle = "1 issue available"
    else:
        subtitle = f"{book_count} issues available (rolling weekly archive)"

    catalog = f'''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:dc="http://purl.org/dc/terms/"
      xmlns:opds="http://opds-spec.org/2010/catalog">

    <id>urn:uuid:bloomberg-daily-opds-feed</id>
    <title>Bloomberg Daily Briefing</title>
    <subtitle>{subtitle}</subtitle>
    <icon>https://assets.bwbx.io/s3/javelin/public/hub/images/favicon-black-63fe5249d3.png</icon>
    <updated>{now}</updated>
    <author>
        <name>Bloomberg News Pipeline</name>
        <uri>https://github.com/MylesMCook/bloomberg-daily</uri>
    </author>

    <link href="opds.xml" rel="self" type="application/atom+xml;profile=opds-catalog;kind=acquisition"/>
    <link href="opds.xml" rel="start" type="application/atom+xml;profile=opds-catalog;kind=acquisition"/>
    {''.join(entries)}
</feed>'''

    return catalog


def main():
    """Main entry point."""
    print(f"Scanning for EPUBs in: {BOOKS_DIR}")

    books = get_books()
    print(f"Found {len(books)} EPUB(s)")

    for book in books:
        print(f"  - {book.name} ({book.stat().st_size / 1024 / 1024:.1f} MB)")

    catalog = generate_catalog()

    OUTPUT_FILE.write_text(catalog, encoding='utf-8')
    print(f"\nGenerated OPDS catalog: {OUTPUT_FILE}")
    print(f"Catalog size: {len(catalog)} bytes")


if __name__ == "__main__":
    main()
