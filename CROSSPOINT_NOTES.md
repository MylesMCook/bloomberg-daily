# CrossPoint Reader Compatibility Notes

## Key Finding (Jan 31, 2026)

**Raw Calibre output works on CrossPoint. Post-processing breaks it.**

The `process_epub.py` script was modifying EPUBs in ways that broke CrossPoint compatibility, even though they worked fine on desktop EPUB readers.

### What Works
- Raw output from `ebook-convert bloomberg_filtered.recipe output.epub --output-profile=generic_eink_hd`
- EPUB transferred via Calibre to device

### What Breaks CrossPoint
- Any EPUB repackaging (even with correct mimetype handling)
- Modifying the OPF manifest
- Stripping/modifying HTML content
- Custom CSS (CrossPoint ignores CSS anyway)

### CrossPoint Rendering
- CrossPoint parses HTML and applies its own font/spacing/alignment
- CSS is ignored - device settings control appearance
- Images are NOT rendered (but including them doesn't break the EPUB)
- Device has limited RAM (380KB) - uses aggressive caching

### Current Setup
- Workflow uses raw Calibre output directly (no post-processing)
- EPUB is ~2MB with images included
- Files served via Railway OPDS server with authentication

### Known Issues to Fix
1. First 2 pages are unnecessary (cover + masthead/sections)
2. Some text spacing issues

### Approach for Fixes
Any fixes should be done in the Calibre recipe itself, NOT by post-processing the EPUB.
Modify `bloomberg_filtered.recipe` to control output at generation time.
