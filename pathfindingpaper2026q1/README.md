# pathfindingpaper2026q1

This folder contains a reproducible downloader for the 34 foundational pathfinding references you listed.

## Contents

- `data/sources.json`: curated source manifest (34 entries).
- `scripts/download_sources.py`: fetches each source URL and stores the response under `papers/`.
- `papers/`: downloaded files (`.pdf` when directly served as PDF, otherwise HTML/landing pages).
- `reports/download_report.json` and `.csv`: per-source status (ok, warning, http_error, etc.).

## Run

```bash
python3 pathfindingpaper2026q1/scripts/download_sources.py
```

## Notes

- Some publishers require subscriptions/login, so direct PDF download is not always possible.
- In those cases, the script still stores the official landing page (when available), preserving authoritative source links in-repo.
