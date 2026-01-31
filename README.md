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
- **Health monitoring** - JSON endpoint for system status
- **Debug mode** - Verbose logging on demand
- **Build diagnostics** - Metadata embedded in each EPUB

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
| `health.json` | System health status endpoint |

## Manual Trigger

To manually fetch today's news:

1. Go to **Actions** tab
2. Select **Fetch Bloomberg Daily**
3. Click **Run workflow**
4. Optionally enable **Debug mode** for verbose logging
5. Wait ~2 minutes for fetch + deploy

## Monitoring & Health

### Health Check Endpoint

```
https://mylesmcook.github.io/bloomberg-daily/health.json
```

Returns system status including book count, sizes, and dates:
```json
{
  "status": "ok",
  "book_count": 5,
  "newest_book": "2026-01-31",
  "total_size_mb": 18.5
}
```

### Diagnostic Manifest

Each EPUB contains `_diagnostics.json` with build metadata:
- `workflow_run_id` - GitHub Actions run ID
- `git_sha` - Commit that built this EPUB
- `build_time` - When the EPUB was created
- `article_count` - Number of articles processed

Extract with: `unzip -p Bloomberg_*.epub _diagnostics.json`

## Troubleshooting

### Debug Mode

Enable verbose logging for any workflow run:
1. Go to **Actions** → **Run workflow**
2. Check **Enable debug mode**
3. View detailed logs in the run output

### Common Issues

| Symptom | Check | Solution |
|---------|-------|----------|
| No new EPUB | health.json `last_update` | Check workflow run logs |
| Empty EPUB | Workflow logs for "VALIDATION FAILED" | Bloomberg may be down |
| Workflow timeout | Calibre fetch step | Bloomberg rate limiting |
| Missing articles | Recipe sections list | Update `ALLOWED_SECTIONS` |

### Debug Artifacts

On workflow failure, debug artifacts are automatically uploaded:
- `temp_output/calibre.log` - Calibre fetch output
- `temp_output/process.log` - EPUB processing output
- `temp_output/opds.log` - Catalog generation output

Find them in the workflow run under **Artifacts**.

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
