import random
import asyncio
from typing import List, Dict

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from scrapers.base import BaseScraper


class StealthScraper(BaseScraper):
    """
    Scraper designed for sites with bot protection.
    Uses stealth techniques to avoid detection.
    """

    async def fetch(self) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            context = await browser.new_context(
                user_agent=self._random_user_agent(),
                viewport={"width": 1280, "height": 800},
            )

            page = await context.new_page()

            # Apply stealth correctly
            stealth = Stealth()
            await stealth.apply_stealth_async(page)

            # Random delay before navigation
            await asyncio.sleep(random.uniform(1, 3))

            await page.goto(self.base_url, timeout=60000)

            # Simulate human-like delay
            await asyncio.sleep(random.uniform(2, 5))

            content = await page.content()

            await browser.close()
            return content

    def parse(self, raw_data: str) -> List[Dict]:
        """
        Placeholder parser (same as SimpleScraper for now).
        """
        return [
            {
                "title": "Stealth Job",
                "company": "Stealth Company",
                "location": "Remote",
                "url": self.base_url,
                "description": "Stealth scraped job",
                "source": "stealth",
            }
        ]

    async def run(self) -> List[Dict]:
        raw_data = await self.fetch()
        return self.parse(raw_data)

    def _random_user_agent(self) -> str:
        """
        Return a random realistic user agent.
        """
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)",
        ]
        return random.choice(agents)