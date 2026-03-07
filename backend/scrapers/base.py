from abc import ABC, abstractmethod
from typing import List, Dict


class BaseScraper(ABC):
    """Abstract base class for news portal scrapers."""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    @property
    @abstractmethod
    def portal_id(self) -> str:
        ...

    @property
    @abstractmethod
    def language(self) -> str:
        ...

    @abstractmethod
    def scrape(self, max_articles: int = 10) -> List[Dict]:
        """Return a list of article dicts with keys:
        title, author, date, url, content, word_count
        """
        ...
