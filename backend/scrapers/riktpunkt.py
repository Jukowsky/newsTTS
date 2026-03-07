import logging
import re
import time
from datetime import datetime
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://riktpunkt.nu/"


class RiktpunktScraper(BaseScraper):
    portal_id = "riktpunkt"
    language = "sv"

    def scrape(self, max_articles: int = 10) -> List[Dict]:
        logger.info("Scraping RiktpunKt…")
        try:
            resp = requests.get(BASE_URL, headers=self.HEADERS, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to fetch RiktpunKt main page: %s", exc)
            return []

        soup = BeautifulSoup(resp.content, "html.parser")

        article_urls: List[str] = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if re.search(r"/\d{4}/\d{2}/", href):
                if href.startswith("/"):
                    href = BASE_URL.rstrip("/") + href
                if href not in article_urls:
                    article_urls.append(href)

        logger.info("Found %d article URLs", len(article_urls))

        articles: List[Dict] = []
        for url in article_urls[:max_articles]:
            try:
                time.sleep(1)
                data = self._fetch_article(url)
                if data:
                    articles.append(data)
            except Exception:
                logger.exception("Error processing article %s", url)

        logger.info("Scraped %d RiktpunKt articles", len(articles))
        return articles

    def _fetch_article(self, url: str) -> Dict | None:
        try:
            resp = requests.get(url, headers=self.HEADERS, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            return None

        soup = BeautifulSoup(resp.content, "html.parser")

        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        else:
            title_tag = soup.find("title")
            if title_tag:
                title = re.sub(r"\s*[-–|]\s*RiktpunKt.*$", "", title_tag.get_text(strip=True))

        category = ""
        page_text = soup.get_text()
        for cat in ("UTRIKES", "INRIKES", "FACKLIGT", "EKONOMI", "KULTUR"):
            if cat in page_text:
                category = cat
                break

        date_match = re.search(r"/(\d{4})/(\d{2})/", url)
        date = f"{date_match.group(1)}-{date_match.group(2)}" if date_match else ""

        content = self._extract_content(soup)
        if not title or len(content) < 100:
            return None

        return {
            "title": title,
            "author": category,
            "date": date,
            "url": url,
            "content": content,
            "word_count": len(content.split()),
        }

    @staticmethod
    def _extract_content(soup: BeautifulSoup) -> str:
        content_div = soup.find("div", class_=re.compile(r"content|article|post"))
        if content_div:
            return re.sub(r"\s+", " ", content_div.get_text(strip=True))

        for tag in soup(["nav", "header", "footer", "aside", "script", "style"]):
            tag.decompose()

        paragraphs = soup.find_all("p")
        parts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
        return "\n\n".join(parts)
