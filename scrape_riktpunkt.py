import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import time

def scrape_news():
    """Scrape news articles with both headlines and full content from riktpunkt.nu"""
    
    base_url = "https://riktpunkt.nu/"
    
    try:
        # Get the main page
        print("Fetching main page...")
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        news_articles = []
        
        # Find all article links on the main page
        article_links = soup.find_all("a", href=True)
        article_urls = []
        
        for link in article_links:
            href = link.get("href")
            # Check if it's a full article URL (contains year/month pattern)
            if href and re.search(r'/\d{4}/\d{2}/', href):
                if href.startswith('/'):
                    href = base_url.rstrip('/') + href
                if href not in article_urls:
                    article_urls.append(href)
        
        print(f"Found {len(article_urls)} article URLs")
        
        # Scrape each article
        for i, url in enumerate(article_urls[:10]):  # Limit to first 10 articles to avoid overloading
            try:
                print(f"Scraping article {i+1}/{min(10, len(article_urls))}: {url}")
                
                # Add delay to be respectful to the server
                time.sleep(1)
                
                article_response = requests.get(url)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.content, "html.parser")
                
                # Extract article data
                article_data = extract_article_content(article_soup, url)
                if article_data:
                    news_articles.append(article_data)
                    
            except requests.RequestException as e:
                print(f"Error fetching article {url}: {e}")
                continue
            except Exception as e:
                print(f"Error processing article {url}: {e}")
                continue
        
        # Save results
        save_results(news_articles)
        
        print(f"Successfully scraped {len(news_articles)} articles")
        return news_articles
        
    except requests.RequestException as e:
        print(f"Error fetching main page: {e}")
        return []

def extract_article_content(soup, url):
    """Extract title, category, date, and content from an article page"""
    
    try:
        # Extract title (usually in h1 or title tag)
        title = ""
        title_tag = soup.find("h1")
        if title_tag:
            title = title_tag.get_text().strip()
        else:
            # Fallback to page title
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text().strip()
                # Remove site name if present
                title = re.sub(r'\s*[-–|]\s*RiktpunKt.*$', '', title)
        
        # Extract category (usually appears before the main content)
        category = ""
        category_patterns = ["UTRIKES", "INRIKES", "FACKLIGT", "EKONOMI", "KULTUR"]
        page_text = soup.get_text()
        for pattern in category_patterns:
            if pattern in page_text:
                category = pattern
                break
        
        # Extract date from URL
        date_match = re.search(r'/(\d{4})/(\d{2})/', url)
        date = ""
        if date_match:
            year, month = date_match.groups()
            date = f"{year}-{month}"
        
        # Extract main content
        content = ""
        
        # Try to find the main article content
        # Method 1: Look for div with article content
        content_div = soup.find("div", class_=re.compile(r"content|article|post"))
        if content_div:
            content = content_div.get_text().strip()
        else:
            # Method 2: Look for the main text content
            # Remove navigation, footer, header elements
            for element in soup(["nav", "header", "footer", "aside", "script", "style"]):
                element.decompose()
            
            # Get all paragraphs
            paragraphs = soup.find_all("p")
            content_parts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 50:  # Filter out short paragraphs
                    content_parts.append(text)
            
            content = "\n\n".join(content_parts)
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content).strip()
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Skip if no meaningful content found
        if not title or len(content) < 100:
            return None
        
        return {
            "title": title,
            "category": category,
            "date": date,
            "url": url,
            "content": content,
            "word_count": len(content.split()),
            "scraped_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def save_results(articles):
    """Save articles in multiple formats"""
    
    # Save as JSON for structured data
    with open("scraped_news.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    # Save as text file for easy reading
    with open("scraped_news.txt", "w", encoding="utf-8") as f:
        if articles:
            for i, article in enumerate(articles, 1):
                f.write(f"=== ARTICLE {i} ===\n")
                f.write(f"Title: {article['title']}\n")
                f.write(f"Category: {article['category']}\n")
                f.write(f"Date: {article['date']}\n")
                f.write(f"URL: {article['url']}\n")
                f.write(f"Word Count: {article['word_count']}\n")
                f.write(f"\nContent:\n{article['content']}\n")
                f.write("\n" + "="*80 + "\n\n")
        else:
            f.write("No articles found with the current scraping method.\n")
    
    # Save content only for TTS (separate files for each article)
    import os
    os.makedirs("articles_for_tts", exist_ok=True)
    
    for i, article in enumerate(articles, 1):
        filename = f"articles_for_tts/article_{i:02d}_{article['date']}_{sanitize_filename(article['title'][:50])}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{article['title']}\n\n")
            f.write(article['content'])

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

if __name__ == "__main__":
    print("Starting news scraping from riktpunkt.nu...")
    articles = scrape_news()
    
    if articles:
        print(f"\nScraping completed successfully!")
        print(f"Found {len(articles)} articles")
        print(f"Total words: {sum(article['word_count'] for article in articles)}")
        print("\nFiles created:")
        print("- scraped_news.json (structured data)")
        print("- scraped_news.txt (readable format)")
        print("- articles_for_tts/ folder (individual files for TTS)")
    else:
        print("No articles could be scraped. Please check the website structure or your internet connection.")