import pytest
import asyncio

from scrapers.simple import SimpleScraper
from scrapers.stealth import StealthScraper


@pytest.mark.asyncio
async def test_simple_scraper_runs():
    scraper = SimpleScraper("https://httpbin.org/html")
    jobs = await scraper.run()

    assert isinstance(jobs, list)
    assert len(jobs) > 0
    assert "title" in jobs[0]
    assert "company" in jobs[0]


@pytest.mark.asyncio
async def test_stealth_scraper_runs():
    scraper = StealthScraper("https://httpbin.org/html")
    jobs = await scraper.run()

    assert isinstance(jobs, list)
    assert len(jobs) > 0
    assert jobs[0]["source"] == "stealth"