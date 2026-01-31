#!/usr/bin/env python3
"""
Bloomberg EPUB Post-Processor for CrossPoint E-Ink Reader

Features:
- Removes first 2 pages (cover + section list)
- Smart title shortening for better TOC display
- Applies Newsreader font + dark mode CSS
- Repackages as clean EPUB

Usage:
    python process_epub.py input.epub output.epub
"""

import os
import re
import sys
import shutil
import zipfile
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

# Configuration
MAX_TITLE_LENGTH = 50  # Max chars before shortening
SCRIPT_DIR = Path(__file__).parent
FONT_DIR = SCRIPT_DIR / "fonts"
CSS_FILE = SCRIPT_DIR / "stylesheet.css"


def smart_shorten_title(title: str, max_len: int = MAX_TITLE_LENGTH) -> str:
    """
    Intelligently shorten article titles for better TOC display.

    Strategy:
    1. Remove common suffixes (Bloomberg, (1), (2), etc.)
    2. Remove redundant prefixes if category already shown
    3. Truncate at natural break points (colon, dash, comma)
    4. If still too long, truncate with ellipsis
    """
    original = title

    # Remove common suffixes
    suffixes_to_remove = [
        r'\s*[-–—]\s*Bloomberg.*$',
        r'\s*\(\d+\)\s*$',  # (1), (2), etc.
        r'\s*\|\s*Bloomberg.*$',
        r'\s*:\s*Markets\s*Wrap\s*$',
    ]
    for pattern in suffixes_to_remove:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)

    # If already short enough, return
    if len(title) <= max_len:
        return title.strip()

    # Try to truncate at natural break points
    break_chars = [':', ' - ', ' – ', ', ']
    for char in break_chars:
        if char in title:
            parts = title.split(char)
            # Keep first part if it's substantial
            if len(parts[0]) >= 20 and len(parts[0]) <= max_len:
                return parts[0].strip()

    # Last resort: hard truncate with ellipsis
    if len(title) > max_len:
        # Try to break at word boundary
        truncated = title[:max_len-3]
        last_space = truncated.rfind(' ')
        if last_space > max_len * 0.6:  # Don't cut too much
            truncated = truncated[:last_space]
        return truncated.strip() + '...'

    return title.strip()


def process_epub(input_path: str, output_path: str):
    """Process an EPUB file with all optimizations."""

    print(f"Processing: {input_path}")

    # Create temp directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Extract EPUB
        print("  Extracting EPUB...")
        with zipfile.ZipFile(input_path, 'r') as zf:
            zf.extractall(temp_path)

        # Find content.opf
        opf_path = None
        for root, dirs, files in os.walk(temp_path):
            for f in files:
                if f.endswith('.opf'):
                    opf_path = Path(root) / f
                    break
            if opf_path:
                break

        if not opf_path:
            raise ValueError("No .opf file found in EPUB")

        opf_dir = opf_path.parent

        # Parse OPF
        print("  Parsing content.opf...")
        ET.register_namespace('', 'http://www.idpf.org/2007/opf')
        ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        tree = ET.parse(opf_path)
        root = tree.getroot()

        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }

        # Find manifest and spine
        manifest = root.find('.//{http://www.idpf.org/2007/opf}manifest')
        spine = root.find('.//{http://www.idpf.org/2007/opf}spine')

        # Get list of spine items
        spine_items = spine.findall('{http://www.idpf.org/2007/opf}itemref')

        # Remove first 2 spine items (titlepage + main index)
        print("  Removing first 2 pages from spine...")
        items_to_remove = []
        for i, item in enumerate(spine_items[:2]):
            items_to_remove.append(item)
            print(f"    Removing spine item {i}: {item.get('idref')}")

        for item in items_to_remove:
            spine.remove(item)

        # Add fonts to manifest if they exist
        if FONT_DIR.exists():
            print("  Adding fonts to manifest...")
            fonts_dir = opf_dir / 'fonts'
            fonts_dir.mkdir(exist_ok=True)

            font_files = [
                'Newsreader_14pt-Regular.ttf',
                'Newsreader_14pt-Italic.ttf',
                'Newsreader_14pt-Bold.ttf',
                'Newsreader_14pt-BoldItalic.ttf',
                'Newsreader_14pt-SemiBold.ttf',
            ]

            for font_file in font_files:
                src = FONT_DIR / font_file
                if src.exists():
                    shutil.copy(src, fonts_dir / font_file)
                    # Add to manifest
                    font_id = f"font-{font_file.replace('.ttf', '').replace('_', '-').lower()}"
                    font_item = ET.SubElement(manifest, '{http://www.idpf.org/2007/opf}item')
                    font_item.set('id', font_id)
                    font_item.set('href', f'fonts/{font_file}')
                    font_item.set('media-type', 'application/x-font-ttf')

        # Update stylesheet with our custom CSS
        if CSS_FILE.exists():
            print("  Updating stylesheet...")
            stylesheet_path = opf_dir / 'stylesheet.css'
            with open(CSS_FILE, 'r', encoding='utf-8') as f:
                custom_css = f.read()
            with open(stylesheet_path, 'w', encoding='utf-8') as f:
                f.write(custom_css)

        # Process TOC for smart titles
        print("  Processing TOC titles...")
        toc_ncx_path = opf_dir / 'toc.ncx'
        if toc_ncx_path.exists():
            process_toc_ncx(toc_ncx_path)

        # Also process nav.xhtml if it exists
        nav_path = opf_dir / 'nav.xhtml'
        if nav_path.exists():
            process_nav_xhtml(nav_path)

        # Save modified OPF
        print("  Saving modified content.opf...")
        tree.write(opf_path, encoding='utf-8', xml_declaration=True)

        # Repackage EPUB
        print("  Repackaging EPUB...")
        create_epub(temp_path, output_path)

    print(f"Done! Output: {output_path}")
    print(f"  Size: {os.path.getsize(output_path):,} bytes")


def process_toc_ncx(toc_path: Path):
    """Process toc.ncx to shorten titles."""
    ET.register_namespace('', 'http://www.daisy.org/z3986/2005/ncx/')
    tree = ET.parse(toc_path)
    root = tree.getroot()

    ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}

    # Find all navLabel/text elements
    for text_elem in root.findall('.//ncx:navLabel/ncx:text', ns):
        if text_elem.text:
            original = text_elem.text
            shortened = smart_shorten_title(text_elem.text)
            if original != shortened:
                text_elem.text = shortened
                print(f"    '{original[:40]}...' -> '{shortened}'")

    tree.write(toc_path, encoding='utf-8', xml_declaration=True)


def process_nav_xhtml(nav_path: Path):
    """Process nav.xhtml to shorten titles."""
    with open(nav_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple regex to find and shorten link text
    def shorten_link(match):
        full = match.group(0)
        text = match.group(1)
        shortened = smart_shorten_title(text)
        return full.replace(f'>{text}<', f'>{shortened}<')

    # Match <a ...>Title Text</a>
    pattern = r'<a[^>]*>([^<]+)</a>'
    content = re.sub(pattern, shorten_link, content)

    with open(nav_path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_epub(source_dir: Path, output_path: str):
    """Create EPUB with proper structure (mimetype first, uncompressed)."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # mimetype must be first and uncompressed
        mimetype_path = source_dir / 'mimetype'
        if mimetype_path.exists():
            zf.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)

        # Add all other files
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file == 'mimetype':
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(source_dir)
                zf.write(file_path, arcname)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python process_epub.py input.epub output.epub")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    process_epub(input_file, output_file)
