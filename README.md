# Job Scraper

Production-quality Python job scraper built with:

- Playwright (browser automation)
- PostgreSQL
- SQLAlchemy
- Typer CLI
- APScheduler
- Docker

## Features

- Scrapes multiple job boards
- Anti-bot stealth scraping
- PostgreSQL storage
- Deduplication logic
- CLI interface
- Scheduled scraping

## Development Setup

### Create virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate