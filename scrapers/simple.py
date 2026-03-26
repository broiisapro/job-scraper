from typing import Any, List
from playwright.async_api import async_playwright

from scrapers.base import BaseScraper


class SimpleScraper(BaseScraper):
    """
    Scraper for simple job boards without heavy anti-bot protection.
    """

    async def fetch(self) -> str:
        """
        Fetch page HTML using Playwright.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(self.base_url)
            content = await page.content()

            await browser.close()
            return content

    def parse(self, raw_data: str) -> List[dict]:
        """
        Placeholder parser (to be improved later).
        """
        # For now, return dummy data
        return [
            {
                "title": "Example Job",
                "company": "Example Company",
                "location": "Remote",
                "url": self.base_url,
                "description": "Placeholder description",
                "source": "example",
            }
        ]

    async def run(self) -> List[dict]:
        """
        Execute full scraping pipeline.
        """
        raw_data = await self.fetch()
        jobs = self.parse(raw_data)
        return jobs