#!/usr/bin/env python3
"""
Bloomberg EPUB Post-Processor for CrossPoint E-Ink Reader

Features:
- Removes first 2 pages (cover + section list)
- Smart title shortening for better TOC display
- Applies Newsreader font + dark mode CSS
- Adds diagnostic manifest for debugging
- Repackages as clean EPUB

Usage:
    python process_epub.py input.epub output.epub

Environment Variables:
    BLOOMBERG_DEBUG - Set to '1', 'true', or 'yes' for verbose logging
    WORKFLOW_RUN_ID - GitHub Actions run ID (for diagnostics)
    GIT_SHA - Git commit SHA (for diagnostics)
"""

import os
import re
import sys
import json
import shutil
import zipfile
import tempfile
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

# ============================================================================
# Logging Configuration
# ============================================================================

DEBUG = os.environ.get('BLOOMBERG_DEBUG', '').lower() in ('1', 'true', 'yes')

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger('process_epub')

if DEBUG:
    log.debug("Debug mode enabled")

# ============================================================================
# Configuration
# ============================================================================

MAX_TITLE_LENGTH = 50  # Max chars before shortening
SCRIPT_DIR = Path(__file__).parent
FONT_DIR = SCRIPT_DIR / "fonts"
CSS_FILE = SCRIPT_DIR / "stylesheet.css"

# ============================================================================
# Input Validation
# ============================================================================

def validate_input(input_path: str) -> Path:
    """Validate input file exists and is a valid EPUB."""
    path = Path(input_path)

    log.info(f"Validating input: {input_path}")

    if not path.exists():
        log.error(f"Input file not found: {input_path}")
        log.error(f"Current working directory: {Path.cwd()}")
        log.error(f"Directory contents: {list(path.parent.glob('*')) if path.parent.exists() else 'parent dir missing'}")
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not path.suffix.lower() == '.epub':
        log.error(f"Input file is not an EPUB: {input_path}")
        raise ValueError(f"Input file must be an EPUB: {input_path}")

    size = path.stat().st_size
    log.info(f"Input file size: {size:,} bytes ({size/1024/1024:.2f} MB)")

    if size < 1000:
        log.error(f"Input file is too small ({size} bytes) - possibly empty or corrupt")
        raise ValueError(f"Input file is too small: {size} bytes")

    # Quick EPUB validation - check if it's a valid zip with mimetype
    try:
        with zipfile.ZipFile(path, 'r') as zf:
            if 'mimetype' not in zf.namelist():
                log.warning("EPUB missing 'mimetype' file - may be malformed")
            names = zf.namelist()
            log.debug(f"EPUB contains {len(names)} files")
    except zipfile.BadZipFile as e:
        log.error(f"Input file is not a valid ZIP/EPUB: {e}")
        raise ValueError(f"Input file is not a valid EPUB: {e}")

    log.info("Input validation passed")
    return path


def validate_output_path(output_path: str) -> Path:
    """Validate output path is writable."""
    path = Path(output_path)

    log.info(f"Validating output path: {output_path}")

    # Ensure parent directory exists
    if not path.parent.exists():
        log.info(f"Creating output directory: {path.parent}")
        path.parent.mkdir(parents=True, exist_ok=True)

    # Check if we can write to the directory
    try:
        test_file = path.parent / f".write_test_{os.getpid()}"
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        log.error(f"Cannot write to output directory: {path.parent}")
        raise PermissionError(f"Cannot write to output directory: {e}")

    log.info("Output path validation passed")
    return path


# ============================================================================
# Title Processing
# ============================================================================

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


# ============================================================================
# Diagnostic Manifest
# ============================================================================

def create_diagnostic_manifest(input_path: Path, output_path: Path, start_time: float,
                               article_count: int = 0, sections: list = None) -> dict:
    """Create diagnostic manifest to embed in EPUB."""
    end_time = time.time()

    manifest = {
        "build_time": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "workflow_run_id": os.environ.get('WORKFLOW_RUN_ID', 'local'),
        "git_sha": os.environ.get('GIT_SHA', 'unknown'),
        "input_file": input_path.name,
        "output_file": output_path.name,
        "raw_size_bytes": input_path.stat().st_size if input_path.exists() else 0,
        "processing_time_ms": int((end_time - start_time) * 1000),
        "debug_mode": DEBUG,
        "python_version": sys.version,
        "sections_found": sections or [],
        "article_count": article_count,
    }

    log.debug(f"Diagnostic manifest: {json.dumps(manifest, indent=2)}")
    return manifest


# ============================================================================
# Image Stripping (CrossPoint doesn't render images)
# ============================================================================

def strip_images(temp_path: Path, manifest, opf_dir: Path) -> int:
    """Remove all images from EPUB - CrossPoint doesn't support them."""
    images_removed = 0

    # Find and remove image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'}
    for img_file in temp_path.rglob('*'):
        if img_file.suffix.lower() in image_extensions:
            # Don't remove cover image (keep for other readers)
            if 'cover' in img_file.name.lower():
                continue
            try:
                img_file.unlink()
                images_removed += 1
                log.debug(f"  Removed: {img_file.name}")
            except Exception as e:
                log.warning(f"  Failed to remove {img_file}: {e}")

    # Remove image references from manifest
    items_to_remove = []
    for item in manifest.findall('{http://www.idpf.org/2007/opf}item'):
        media_type = item.get('media-type', '')
        href = item.get('href', '')
        if media_type.startswith('image/') and 'cover' not in href.lower():
            items_to_remove.append(item)

    for item in items_to_remove:
        manifest.remove(item)

    # Remove <img> tags from HTML files
    for html_file in temp_path.rglob('*.html'):
        strip_img_tags(html_file)
    for xhtml_file in temp_path.rglob('*.xhtml'):
        strip_img_tags(xhtml_file)

    return images_removed


def strip_img_tags(html_path: Path):
    """Remove <img> tags from HTML file."""
    try:
        content = html_path.read_text(encoding='utf-8')
        # Simple regex to remove img tags (keeps cover references)
        import re
        # Remove img tags that don't reference cover
        content = re.sub(r'<img[^>]*(?<!cover)[^>]*/?>', '', content, flags=re.IGNORECASE)
        # Also remove figure elements that contained images
        content = re.sub(r'<figure[^>]*>\s*</figure>', '', content, flags=re.IGNORECASE)
        # Remove empty divs that might have held images
        content = re.sub(r'<div[^>]*class="[^"]*img[^"]*"[^>]*>\s*</div>', '', content, flags=re.IGNORECASE)
        html_path.write_text(content, encoding='utf-8')
    except Exception as e:
        log.warning(f"Failed to process {html_path}: {e}")


# ============================================================================
# EPUB Processing
# ============================================================================

def process_epub(input_path: str, output_path: str):
    """Process an EPUB file with all optimizations."""
    start_time = time.time()

    log.info("=" * 60)
    log.info("Bloomberg EPUB Processor")
    log.info("=" * 60)

    # Validate inputs
    input_path = validate_input(input_path)
    output_path = validate_output_path(output_path)

    log.info(f"Processing: {input_path}")
    log.info(f"Output: {output_path}")

    article_count = 0
    sections_found = []

    # Create temp directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Extract EPUB
        log.info("Extracting EPUB...")
        try:
            with zipfile.ZipFile(input_path, 'r') as zf:
                zf.extractall(temp_path)
            log.debug(f"Extracted to: {temp_path}")
        except Exception as e:
            log.error(f"Failed to extract EPUB: {e}")
            log.error(f"Input file: {input_path}")
            log.error(f"Input size: {input_path.stat().st_size}")
            raise

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
            log.error("No .opf file found in EPUB")
            log.error(f"Temp directory contents: {list(temp_path.rglob('*'))}")
            raise ValueError("No .opf file found in EPUB")

        opf_dir = opf_path.parent
        log.debug(f"Found OPF at: {opf_path}")

        # Parse OPF
        log.info("Parsing content.opf...")
        try:
            ET.register_namespace('', 'http://www.idpf.org/2007/opf')
            ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
            tree = ET.parse(opf_path)
            root = tree.getroot()
        except Exception as e:
            log.error(f"Failed to parse OPF: {e}")
            log.error(f"OPF path: {opf_path}")
            raise

        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }

        # Find manifest and spine
        manifest = root.find('.//{http://www.idpf.org/2007/opf}manifest')
        spine = root.find('.//{http://www.idpf.org/2007/opf}spine')

        if spine is None:
            log.error("No spine element found in OPF")
            raise ValueError("Invalid EPUB: no spine element")

        # Get list of spine items
        spine_items = spine.findall('{http://www.idpf.org/2007/opf}itemref')
        log.info(f"Found {len(spine_items)} spine items")

        # Count articles (rough estimate from spine)
        article_count = max(0, len(spine_items) - 2)

        # Remove first 2 spine items (titlepage + main index)
        log.info("Removing first 2 pages from spine...")
        items_to_remove = []
        for i, item in enumerate(spine_items[:2]):
            items_to_remove.append(item)
            log.debug(f"  Removing spine item {i}: {item.get('idref')}")

        for item in items_to_remove:
            spine.remove(item)

        # Strip all images (CrossPoint doesn't render them)
        log.info("Stripping images (not supported by CrossPoint)...")
        images_removed = strip_images(temp_path, manifest, opf_dir)
        log.info(f"  Removed {images_removed} images")

        # Skip fonts - CrossPoint uses its own native fonts

        # Update stylesheet with our custom CSS
        if CSS_FILE.exists():
            log.info("Updating stylesheet...")
            stylesheet_path = opf_dir / 'stylesheet.css'
            with open(CSS_FILE, 'r', encoding='utf-8') as f:
                custom_css = f.read()
            with open(stylesheet_path, 'w', encoding='utf-8') as f:
                f.write(custom_css)
            log.debug(f"  CSS size: {len(custom_css)} bytes")
        else:
            log.warning(f"CSS file not found: {CSS_FILE}")

        # Process TOC for smart titles
        log.info("Processing TOC titles...")
        toc_ncx_path = opf_dir / 'toc.ncx'
        if toc_ncx_path.exists():
            process_toc_ncx(toc_ncx_path)

        # Also process nav.xhtml if it exists
        nav_path = opf_dir / 'nav.xhtml'
        if nav_path.exists():
            process_nav_xhtml(nav_path)

        # Add diagnostic manifest
        log.info("Adding diagnostic manifest...")
        diagnostics = create_diagnostic_manifest(
            input_path, output_path, start_time,
            article_count=article_count, sections=sections_found
        )
        diagnostics_path = opf_dir / '_diagnostics.json'
        diagnostics_path.write_text(json.dumps(diagnostics, indent=2), encoding='utf-8')

        # Add diagnostics to manifest
        diag_item = ET.SubElement(manifest, '{http://www.idpf.org/2007/opf}item')
        diag_item.set('id', 'diagnostics')
        diag_item.set('href', '_diagnostics.json')
        diag_item.set('media-type', 'application/json')

        # Save modified OPF
        log.info("Saving modified content.opf...")
        tree.write(opf_path, encoding='utf-8', xml_declaration=True)

        # Repackage EPUB
        log.info("Repackaging EPUB...")
        create_epub(temp_path, output_path)

    # Final stats
    final_size = output_path.stat().st_size
    processing_time = time.time() - start_time

    log.info("=" * 60)
    log.info("Processing complete!")
    log.info("=" * 60)
    log.info(f"Output: {output_path}")
    log.info(f"Size: {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
    log.info(f"Processing time: {processing_time:.2f}s")


def process_toc_ncx(toc_path: Path):
    """Process toc.ncx to shorten titles."""
    log.debug(f"Processing TOC NCX: {toc_path}")

    try:
        ET.register_namespace('', 'http://www.daisy.org/z3986/2005/ncx/')
        tree = ET.parse(toc_path)
        root = tree.getroot()

        ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}

        # Find all navLabel/text elements
        modified_count = 0
        for text_elem in root.findall('.//ncx:navLabel/ncx:text', ns):
            if text_elem.text:
                original = text_elem.text
                shortened = smart_shorten_title(text_elem.text)
                if original != shortened:
                    text_elem.text = shortened
                    modified_count += 1
                    if DEBUG:
                        log.debug(f"  '{original[:30]}...' -> '{shortened}'")

        tree.write(toc_path, encoding='utf-8', xml_declaration=True)
        log.info(f"  Modified {modified_count} TOC entries")

    except Exception as e:
        log.error(f"Failed to process TOC NCX: {e}")
        log.error(f"TOC path: {toc_path}")
        # Don't fail the whole process for TOC issues
        log.warning("Continuing without TOC modifications")


def process_nav_xhtml(nav_path: Path):
    """Process nav.xhtml to shorten titles."""
    log.debug(f"Processing NAV XHTML: {nav_path}")

    try:
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

        log.info("  NAV XHTML processed")

    except Exception as e:
        log.error(f"Failed to process NAV XHTML: {e}")
        log.warning("Continuing without NAV modifications")


def create_epub(source_dir: Path, output_path: str):
    """Create EPUB with proper structure (mimetype first, uncompressed)."""
    log.debug(f"Creating EPUB: {output_path}")

    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # mimetype must be first and uncompressed
            mimetype_path = source_dir / 'mimetype'
            if mimetype_path.exists():
                zf.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)

            # Add all other files
            file_count = 0
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if file == 'mimetype':
                        continue
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(source_dir)
                    zf.write(file_path, arcname)
                    file_count += 1

            log.debug(f"  Packed {file_count} files")

    except Exception as e:
        log.error(f"Failed to create EPUB: {e}")
        log.error(f"Source dir: {source_dir}")
        log.error(f"Output path: {output_path}")
        raise


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python process_epub.py input.epub output.epub")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        process_epub(input_file, output_file)
    except Exception as e:
        log.error(f"FATAL ERROR: {e}")
        sys.exit(1)
