from typing import List, Dict, Callable, Awaitable
import asyncio

from playwright.async_api import async_playwright

from scrapers.base import BaseScraper


class SimpleScraper(BaseScraper):
    """
    Scraper for simple job boards without heavy anti-bot protection.
    """

    async def _retry(
        self,
        func: Callable[[], Awaitable],
        retries: int = 3,
        delay: float = 2.0,
    ):
        """
        Retry wrapper for async operations.
        """
        for attempt in range(retries):
            try:
                return await func()
            except Exception:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(delay)

    async def fetch(self, url: str) -> str:
        """
        Fetch page HTML using Playwright with retry logic.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await self._retry(lambda: page.goto(url, timeout=60000))

            content = await page.content()

            await browser.close()
            return content

    def parse(self, raw_data: str, url: str) -> List[Dict]:
        """
        Placeholder parser (to be improved later).
        """
        return [
            {
                "title": "Example Job",
                "company": "Example Company",
                "location": "Remote",
                "url": url,
                "description": "Placeholder description",
                "source": "example",
            }
        ]

    async def run(self) -> List[Dict]:
        """
        Execute full scraping pipeline with basic pagination.
        """
        all_jobs: List[Dict] = []

        # Simulated pagination (structure ready for real sites)
        for page_num in range(1, 4):
            url = f"{self.base_url}?page={page_num}"

            raw_data = await self.fetch(url)
            jobs = self.parse(raw_data, url)

            all_jobs.extend(jobs)

        return all_jobs