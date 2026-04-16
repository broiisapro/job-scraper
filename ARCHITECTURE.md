# Architecture Overview

## System Summary

This project is a modular job scraping system designed to collect, normalize, and store job listings from multiple sources with support for anti-bot evasion, deduplication, and scheduled execution.

The architecture is intentionally layered and config-driven so new data sources can be introduced with minimal code changes. The design prioritizes reliability (idempotent ingestion), maintainability (clear separation of concerns), and operational flexibility (CLI + scheduler execution paths).

---

## Core Components

### 1. Scraper Layer (Strategy Pattern)

The system uses a strategy pattern to support multiple scraping approaches:

- `BaseScraper`: Abstract interface defining `fetch`, `parse`, and `run`
- `SimpleScraper`: Used for public job boards
- `StealthScraper`: Uses anti-bot techniques (playwright-stealth, delays, user-agent rotation)

This allows new scrapers to be added without modifying existing logic.

#### Typical Scraper Lifecycle

1. Load site configuration from `sites.yaml`
2. Initialize scraper strategy (`SimpleScraper` or `StealthScraper`)
3. Fetch raw listing pages with retry and pagination
4. Parse structured job records
5. Normalize records into a canonical schema
6. Persist with deduplication guarantees

---

### 2. Configuration System

- `.env` -> environment configuration (database, secrets)
- `sites.yaml` -> per-site scraping configuration

This separation enables flexible, scalable multi-site scraping without hardcoding behavior.

#### Configuration Principles

- Environment variables hold sensitive/runtime concerns (credentials, endpoints, toggles)
- YAML holds site-specific behavior (selectors, pagination, scraping mode)
- Defaults should remain safe for local development and CI

---

### 3. Database Layer

- PostgreSQL (Dockerized)
- SQLAlchemy ORM (typed models)
- Alembic migrations for schema versioning

#### Deduplication Strategy

Jobs are deduplicated at the database level using:

- Unique constraint on `url`
- PostgreSQL `ON CONFLICT DO NOTHING`

This ensures idempotent ingestion and prevents race conditions.

#### Data Integrity Goals

- Keep writes idempotent across retries and scheduled runs
- Preserve immutable source metadata where useful for auditing
- Version schema changes with forward-only migration discipline

---

### 4. CLI Interface

Built with Typer + Rich:

- `run` -> execute all scrapers
- `search` -> view stored jobs
- `export` -> export to JSON
- `stats` -> view aggregated metrics

This transforms the system into a usable developer tool.

#### CLI Design Notes

- Commands are composable and script-friendly
- Output is human-readable for local usage and debuggability
- CLI serves as the shared execution surface for both manual and scheduled runs

---

### 5. Scheduler

- APScheduler-based cron system
- Reuses CLI logic to avoid duplication

Enables automated periodic scraping.

#### Scheduling Considerations

- Jobs should be safe to rerun due to DB-level deduplication
- Failures should be logged with enough context for rapid diagnosis
- Per-site schedules can be tuned based on source volatility and rate limits

---

### 6. Data Pipeline

Scraper -> Parsed Jobs -> Normalization -> Database (deduplicated)
Includes retry logic and pagination support for resilience.

#### Pipeline Guarantees

- Canonical normalization before persistence
- Stable identifiers for deduplication
- Controlled retries to handle transient network/source failures

---

### 7. CI/CD

- GitHub Actions
- Runs linting (ruff) and tests (pytest)
- Uses PostgreSQL service container

Ensures reliability across environments.

#### Quality Gates

- Linting enforces consistent style and catches common issues early
- Automated tests validate parser behavior and DB interactions
- CI-backed database service reduces environment drift between local and pipeline runs

---

## Design Decisions

### Why Strategy Pattern?

Allows multiple scraping implementations without conditional logic.

### Why DB-Level Deduplication?

- Atomic
- Safe under concurrency
- More efficient than application-level checks

### Why Playwright?

- Handles dynamic content
- Required for modern job boards

### Why Config-Driven Design?

Enables scaling to multiple sites without modifying code.

---

## Operational Concerns

### Error Handling and Retries

- Transient failures should trigger bounded retry logic
- Persistent failures should surface clear logs and metrics
- Source-specific failures should not block the entire run when isolation is possible

### Observability

- Structured logs per scraper/site/run
- Basic run metrics: fetched, parsed, inserted, deduplicated, failed
- Optional alerting hooks for repeated site failures

### Security and Compliance

- Keep secrets in environment configuration, never in source control
- Respect source Terms of Service and rate limits
- Use anti-bot techniques responsibly and with operational safeguards

---

## Future Improvements

- Proxy rotation
- Headless browser pooling
- Distributed scraping workers
- Advanced parsing per site
- Salary normalization stored in DB
- Site health scoring and adaptive backoff
- Event-driven ingestion pipeline (queue-based execution)
- Change-data capture for job updates and expiration tracking

---

## Conclusion

This system is designed to reflect real-world scraping architectures, focusing on scalability, reliability, and maintainability.

Its layered design, configuration-first approach, and idempotent persistence strategy make it suitable for incremental growth from a single-node workflow to a larger multi-source ingestion platform.
