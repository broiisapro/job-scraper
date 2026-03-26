from abc import ABC, abstractmethod
from typing import Any, List


class BaseScraper(ABC):
    """
    Abstract base class for all job scrapers.
    Defines the interface that all scraper implementations must follow.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    @abstractmethod
    async def fetch(self) -> Any:
        """
        Fetch raw data from the source.
        """
        raise NotImplementedError

    @abstractmethod
    def parse(self, raw_data: Any) -> List[dict]:
        """
        Parse raw data into structured job records.
        """
        raise NotImplementedError

    @abstractmethod
    async def run(self) -> List[dict]:
        """
        Full scraping pipeline: fetch → parse.
        """
        raise NotImplementedError