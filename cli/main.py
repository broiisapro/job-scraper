import asyncio
from typing import List

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config.loader import load_sites_config
from scrapers.simple import SimpleScraper
from scrapers.stealth import StealthScraper
from db.queries import upsert_jobs


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

            # ✅ Correct async execution
            jobs = asyncio.run(scraper.run())

            inserted = upsert_jobs(jobs)
            total_inserted += inserted

            progress.update(task, description=f"{name} complete ({inserted} new jobs)")

    console.print(f"[green]Done. Total new jobs: {total_inserted}[/green]")


if __name__ == "__main__":
    app()