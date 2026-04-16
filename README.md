# Job Scraper

A production-oriented job scraping system designed to mirror real-world data pipelines: scrape, normalize, and persist structured records with reliability and extensibility in mind.

This project is intentionally built as a system, not a one-off script.

## Overview

The scraper collects job listing data from web sources, transforms raw page content into normalized job records, and writes those records to PostgreSQL using idempotent database operations.

It is designed around modular boundaries so each layer can evolve independently:

- Scraping strategy layer for source-specific behavior
- Parsing and normalization layer for structured output
- Database layer for durable, deduplicated storage
- Configuration layer for environment and site behavior

## Why This Project Exists

Many scraper projects break down because they are tightly coupled and hard to extend. This project addresses that by:

- Isolating scrape behavior behind a shared scraper interface
- Using database-level deduplication instead of fragile in-memory checks
- Separating runtime settings (`.env`) from site config (`config/sites.yaml`)
- Building on production-grade tooling (Playwright, SQLAlchemy, Alembic, PostgreSQL)

## System Capabilities

- Async browser automation with Playwright
- Multiple scraping strategies (`SimpleScraper`, `StealthScraper`)
- Structured ORM model for job data
- PostgreSQL upsert flow with conflict-safe inserts
- Config-driven site definitions via YAML
- Environment-driven settings via Pydantic Settings
- Automated tests for scraper behavior

## Product Snapshot

The following highlights capture the intended production shape of this project and the architecture direction it is built toward.

### 🚀 Features

- Multi-site job scraping (config-driven)
- Playwright-based browser automation
- Stealth scraping for protected sites
- PostgreSQL storage with deduplication
- CLI interface (run, search, export, stats)
- Scheduled scraping (APScheduler)
- Retry logic + pagination support
- CI pipeline with linting and tests

---

### 🧱 Architecture Highlights

- Strategy pattern for scraper implementations
- Database-level deduplication (PostgreSQL `ON CONFLICT`)
- Separation of config (`.env` vs YAML)
- Async scraping pipeline with Playwright
- Modular, extensible design

---

### 🛠️ Tech Stack

- Python 3.12
- Playwright + `playwright-stealth`
- SQLAlchemy + Alembic
- PostgreSQL (Docker)
- Typer + Rich
- APScheduler
- Pytest + Ruff
- GitHub Actions

### Implementation Notes

- The repository already includes core scraping, normalization, and persistence building blocks.
- CLI and scheduler capabilities are part of the intended architecture and can be wired through the same modular layers already present.
- The current structure is designed so new sites, strategies, and operational workflows can be added without rewriting core components.

## Architecture

```text
Application Entry (script / future CLI / future scheduler)
                    |
                    v
         Scraper Layer (Strategy Pattern)
      +----------------+----------------+
      |                                 |
SimpleScraper                     StealthScraper
      |                                 |
      +---------------+-----------------+
                      v
            Parse / Normalize Jobs
                      |
                      v
          Database Queries (SQLAlchemy)
                      |
                      v
                 PostgreSQL
```

### Core Components

- `scrapers/base.py`: Abstract scraper contract (`fetch`, `parse`, `run`)
- `scrapers/simple.py`: Standard Playwright strategy for low-friction targets
- `scrapers/stealth.py`: Stealth-enhanced strategy for bot-protected targets
- `db/models.py`: `Job` ORM model + uniqueness constraint on `url`
- `db/queries.py`: `upsert_jobs()` write path using PostgreSQL conflict handling
- `config/settings.py`: `.env`-driven runtime settings
- `config/loader.py` + `config/sites.yaml`: Site-level scrape configuration

## Data Flow

```text
1) Read site metadata from config/sites.yaml
2) Select scraper strategy (simple / stealth)
3) Fetch HTML with Playwright
4) Parse HTML into normalized job dicts
5) Write jobs through db/queries.upsert_jobs()
6) PostgreSQL enforces URL uniqueness during insert
```

This produces repeatable ingestion runs where duplicate records are safely ignored at write time.

## Scraper Strategies

This project uses a strategy pattern to support multiple scraping approaches.

### `SimpleScraper`

- Uses Playwright for basic page rendering
- Designed for public job boards without strong bot protection
- Fast and lightweight

### `StealthScraper`

- Uses `playwright-stealth` to reduce bot-detection signals
- Randomizes user agents and introduces human-like delays
- Designed for protected sites (for example, Indeed and LinkedIn-like targets)

This separation allows adding new strategy classes without changing existing scraper implementations.

## Tech Stack

- Python 3.12
- Playwright + `playwright-stealth`
- PostgreSQL (Docker)
- SQLAlchemy 2.x + Alembic
- Pydantic + `pydantic-settings`
- YAML site configuration
- `pytest` + `pytest-asyncio`

## Setup

### 1) Create environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2) Install project

```bash
pip install -e ".[dev]"
python -m playwright install
```

### 3) Start PostgreSQL

```bash
docker compose up -d
```

### 4) Configure environment

Create `.env` in the project root:

```env
DATABASE_URL=postgresql+psycopg2://scraper:scraper@localhost:5432/jobs
```

## Usage

### Programmatic run example

```python
import asyncio

from db.queries import upsert_jobs
from scrapers.simple import SimpleScraper


async def main() -> None:
    scraper = SimpleScraper("https://httpbin.org/html")
    jobs = await scraper.run()
    inserted = upsert_jobs(jobs)
    print(f"Rows affected: {inserted}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Run tests

```bash
pytest
```

## Design Decisions

### 1) Database-level deduplication

Deduplication is handled in PostgreSQL rather than Python loops:

- `UNIQUE` constraint on `jobs.url` in `db/models.py`
- `ON CONFLICT DO NOTHING` in `db/queries.py`

Why this matters:

- Atomic behavior under concurrent writers
- Reduced race-condition risk
- Consistent data integrity at the storage boundary

### 2) Strategy pattern for scraper behavior

All scrapers implement a shared contract via `BaseScraper`:

- `fetch()`
- `parse()`
- `run()`

Why this matters:

- Easy to add new site-specific strategies
- Minimal impact on existing code
- Better testability and separation of concerns

### 3) Config separation

- `.env`: operational environment values (for example `DATABASE_URL`)
- `config/sites.yaml`: per-site scrape targets and behavior

Why this matters:

- Cleaner deployment and local development
- Easier scaling to many targets
- Lower coupling between code and runtime configuration

## Roadmap

- Add a Typer-based CLI entrypoint for scrape commands
- Add APScheduler jobs for periodic runs
- Implement retry + backoff for transient failures
- Add proxy rotation support for resilient scraping
- Expand parser logic beyond placeholder records
- Add metrics/logging for scrape quality and throughput

## Author

Moksh - building production-style systems focused on practical engineering problems.
