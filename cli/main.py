import asyncio
import json

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config.loader import load_sites_config
from scrapers.simple import SimpleScraper
from scrapers.stealth import StealthScraper
from db.queries import upsert_jobs, get_jobs

from sqlalchemy import func
from db.session import SessionLocal
from db.models import Job

app = typer.Typer()
console = Console()


def get_scraper(scraper_type: str, base_url: str):
    """
    Factory function to return the correct scraper.
    """
    if scraper_type == "simple":
        return SimpleScraper(base_url)
    elif scraper_type == "stealth":
        return StealthScraper(base_url)
    else:
        raise ValueError(f"Unknown scraper type: {scraper_type}")

@app.command()
def stats():
    """
    Show statistics about stored jobs.
    """
    session = SessionLocal()

    try:
        total = session.query(func.count(Job.id)).scalar()
        sources = session.query(Job.source, func.count()).group_by(Job.source).all()

        console.print(f"[bold]Total jobs:[/bold] {total}")

        console.print("\n[bold]Jobs by source:[/bold]")
        for source, count in sources:
            console.print(f"{source}: {count}")

    finally:
        session.close()

@app.command()
def run() -> None:
    """
    Run all configured scrapers.
    """
    config = load_sites_config()
    sites = config.get("sites", {})

    if not sites:
        console.print("[red]No sites configured.[/red]")
        raise typer.Exit(code=1)

    total_inserted = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        for site_key, site_config in sites.items():
            name = site_config["name"]
            base_url = site_config["base_url"]
            scraper_type = site_config["type"]

            task = progress.add_task(f"Scraping {name}...", start=True)

            scraper = get_scraper(scraper_type, base_url)

            jobs = asyncio.run(scraper.run())

            inserted = upsert_jobs(jobs)
            total_inserted += inserted

            progress.update(task, description=f"{name} complete ({inserted} new jobs)")

    console.print(f"[green]Done. Total new jobs: {total_inserted}[/green]")


@app.command()
def search(limit: int = 10):
    """
    Search stored jobs.
    """
    jobs = get_jobs(limit)

    if not jobs:
        console.print("[red]No jobs found.[/red]")
        return

    for job in jobs:
        console.print(f"[bold]{job.title}[/bold]")
        console.print(f"{job.company} | {job.location}")
        console.print(f"{job.url}")
        console.print("-" * 40)


@app.command()
def export(file: str = "jobs.json"):
    """
    Export jobs to JSON file.
    """
    jobs = get_jobs(100)

    data = [
        {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "url": job.url,
            "description": job.description,
            "source": job.source,
        }
        for job in jobs
    ]

    with open(file, "w") as f:
        json.dump(data, f, indent=2)

    console.print(f"[green]Exported {len(data)} jobs to {file}[/green]")


if __name__ == "__main__":
    app()