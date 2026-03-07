import logging
import re
import time
from typing import List, Dict

import cloudscraper
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://haber.sol.org.tr"
LISTING_URL = f"{BASE_URL}/kose-yazilari"


class SolScraper(BaseScraper):
    portal_id = "sol"
    language = "tr"

    def __init__(self):
        self._session = cloudscraper.create_scraper()

    def scrape(self, max_articles: int = 10) -> List[Dict]:
        logger.info("Scraping Sol Haber columns…")
        try:
            resp = self._session.get(LISTING_URL, timeout=30)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("Failed to fetch Sol listing: %s", exc)
            return []

        soup = BeautifulSoup(resp.content, "html.parser")
        items = soup.select("div.item")
        logger.info("Found %d items on listing page", len(items))

        articles: List[Dict] = []
        for item in items[:max_articles]:
            try:
                meta = self._parse_listing_item(item)
                if not meta:
                    continue

                time.sleep(1)
                content = self._fetch_article_content(meta["url"])
                if not content:
                    continue

                meta["content"] = content
                meta["word_count"] = len(content.split())
                articles.append(meta)
            except Exception:
                logger.exception("Error processing Sol listing item")

        logger.info("Scraped %d Sol articles", len(articles))
        return articles

    def _parse_listing_item(self, item) -> Dict | None:
        h2 = item.find("h2")
        author = h2.get_text(strip=True) if h2 else ""

        h3 = item.find("h3")
        if not h3:
            return None
        link = h3.find("a", href=True)
        if not link:
            return None

        title = link.get_text(strip=True)
        url = link["href"]
        if not url.startswith("http"):
            url = BASE_URL + url

        date_tag = item.find("p", class_=re.compile(r"source"))
        date = date_tag.get_text(strip=True) if date_tag else ""

        return {"title": title, "author": author, "date": date, "url": url}

    def _fetch_article_content(self, url: str) -> str | None:
        try:
            resp = self._session.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("Failed to fetch article %s: %s", url, exc)
            return None

        soup = BeautifulSoup(resp.content, "html.parser")

        body_div = soup.find("div", class_="node-body")
        if not body_div:
            logger.warning("No node-body found for %s", url)
            return None

        paragraphs = body_div.find_all("p")
        texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        content = "\n\n".join(texts)

        if len(content) < 100:
            logger.warning("Content too short for %s (%d chars)", url, len(content))
            return None

        return content
