# Bloomberg Daily Briefing

Automated daily news delivery from Bloomberg, optimized for e-ink readers.

## OPDS Feed

```
https://mylesmcook.github.io/bloomberg-daily/opds.xml
```

Add this URL to your e-reader's OPDS browser to automatically sync daily briefings.

## Features

- **Automated daily fetch** - Runs weekdays at 6:00 AM CST
- **E-ink optimized** - Custom CSS and fonts (Newsreader) for readable typography
- **Curated sections** - AI, Technology, Industries, Latest
- **Rolling archive** - Last 7 issues always available
- **Zero maintenance** - Fully automated via GitHub Actions + Pages
- **Dark mode support** - Automatic theme switching via CSS media queries

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  GitHub Actions │────▶│  GitHub Pages    │────▶│  E-ink Reader   │
│  (6am weekdays) │     │  (Static OPDS)   │     │  (CrossPoint)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                        │
        │                        │
        ▼                        ▼
   Fetch & Process          Serve EPUBs
   Bloomberg News           via OPDS 1.2
```

## Files

| File | Purpose |
|------|---------|
| `bloomberg_filtered.recipe` | Calibre recipe for fetching Bloomberg |
| `process_epub.py` | Post-processor for CSS/fonts/cleanup |
| `generate_opds.py` | OPDS catalog generator |
| `cleanup_old_books.py` | Maintains 7-day rolling archive |
| `stylesheet.css` | E-ink optimized styles with dark mode |
| `fonts/` | Newsreader font family (Google Fonts) |
| `books/` | EPUB archive (auto-managed) |
| `opds.xml` | Generated OPDS catalog |

## Manual Trigger

To manually fetch today's news:

1. Go to **Actions** tab
2. Select **Fetch Bloomberg Daily**
3. Click **Run workflow**
4. Wait ~2 minutes for fetch + deploy

## Sections Included

- **AI** - Artificial intelligence and machine learning news
- **Technology** - Tech industry coverage
- **Industries** - Business and sector news
- **Latest** - Breaking news and updates

## Device Setup (CrossPoint OS)

1. Open **OPDS Browser** on your device
2. Add new catalog with URL: `https://mylesmcook.github.io/bloomberg-daily/opds.xml`
3. No authentication required
4. Set auto-sync schedule as desired

## Configuration

### Change sections
Edit `bloomberg_filtered.recipe`:
```python
ALLOWED_SECTIONS = ['ai', 'technology', 'industries', 'latest']
```

### Change schedule
Edit `.github/workflows/fetch-bloomberg.yml`:
```yaml
schedule:
  - cron: '0 12 * * 1-5'  # 12:00 UTC = 6:00 AM CST, Mon-Fri
```

### Change archive size
Edit the workflow or `cleanup_old_books.py`:
```bash
python cleanup_old_books.py --keep 7  # Keep last 7 issues
```

## Local Development

```bash
# Install Calibre first (https://calibre-ebook.com)

# Fetch and process
ebook-convert bloomberg_filtered.recipe output/Bloomberg_Raw.epub --output-profile=generic_eink_hd
python process_epub.py output/Bloomberg_Raw.epub books/Bloomberg_$(date +%Y-%m-%d).epub

# Generate catalog
python generate_opds.py
```

---

*Powered by Calibre, GitHub Actions, and GitHub Pages*

*For personal use only. Bloomberg content © Bloomberg L.P.*
