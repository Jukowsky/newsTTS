import requests
from bs4 import BeautifulSoup
import os
import json
import logging
from datetime import datetime
import schedule
import time
from typing import List, Dict, Optional

# TTS Integration - Using OpenAI TTS as it supports Turkish
import openai
from openai import OpenAIError

# Import configuration
from config import (
    NEWS_SOURCE, TTS_CONFIG, SCHEDULE_CONFIG, 
    FILE_CONFIG, REQUEST_CONFIG, LOGGING_CONFIG
)

class NewsTTSApp:
    def __init__(self):
        self.setup_logging()
        self.output_dir = FILE_CONFIG['output_directory']
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Initialize OpenAI client
        self.client = openai.OpenAI()
        
        # Request session for better performance
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': REQUEST_CONFIG['user_agent']})
        
        self.logger.info("NewsTTSApp initialized successfully")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['level']),
            format=LOGGING_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOGGING_CONFIG['file']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_column_content(self, url: str) -> Optional[str]:
        """Extract full content from a column article"""
        try:
            self.logger.debug(f"Fetching content from: {url}")
            response = self.session.get(
                url, 
                timeout=REQUEST_CONFIG['timeout']
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for article content
            content_selectors = NEWS_SOURCE['selectors']['content']
            
            content = ""
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    paragraphs = content_div.find_all('p')
                    content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
                    break
            
            if not content:
                self.logger.warning(f"No content found for URL: {url}")
                return "Content could not be extracted"
            
            self.logger.debug(f"Extracted {len(content)} characters from {url}")
            return content
            
        except requests.RequestException as e:
            self.logger.error(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def get_daily_sabah_columns(self) -> List[Dict]:
        """Scrape columns from Daily Sabah"""
        url = NEWS_SOURCE['url']
        try:
            self.logger.info(f"Scraping columns from: {url}")
            response = self.session.get(
                url, 
                timeout=REQUEST_CONFIG['timeout']
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            columns_data = []
            
            # Look for article cards
            selectors = NEWS_SOURCE['selectors']
            article_cards = soup.select(selectors['article_cards'])
            
            if not article_cards:
                self.logger.warning("No article cards found, trying alternative method")
                # Fallback: look for column links directly
                column_links = soup.find_all('a', href=True)
                
                for link in column_links:
                    href = link.get('href')
                    if href and '/columns/' in href and not href.endswith('/columns'):
                        title = link.text.strip()
                        if len(title) > 10:  # Filter out short/empty titles
                            full_url = href if href.startswith('http') else f"https://www.dailysabah.com{href}"
                            
                            # Add delay between requests
                            time.sleep(REQUEST_CONFIG['delay_between_requests'])
                            content = self.get_column_content(full_url)
                            
                            if content and content != "Content could not be extracted":
                                columns_data.append({
                                    'title': title,
                                    'author': 'Unknown',
                                    'url': full_url,
                                    'content': content,
                                    'date': datetime.now().strftime('%Y-%m-%d')
                                })
                                
                                if len(columns_data) >= FILE_CONFIG['max_columns_per_day']:
                                    break
            else:
                # Process article cards
                for card in article_cards:
                    title_elem = card.select_one(selectors['title'])
                    author_elem = card.select_one(selectors['author'])
                    link_elem = card.select_one(selectors['link'])
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        author = author_elem.text.strip() if author_elem else 'Unknown'
                        link = link_elem.get('href')
                        
                        full_url = link if link.startswith('http') else f"https://www.dailysabah.com{link}"
                        
                        # Add delay between requests
                        time.sleep(REQUEST_CONFIG['delay_between_requests'])
                        content = self.get_column_content(full_url)
                        
                        if content and content != "Content could not be extracted":
                            columns_data.append({
                                'title': title,
                                'author': author,
                                'url': full_url,
                                'content': content,
                                'date': datetime.now().strftime('%Y-%m-%d')
                            })
                            
                            if len(columns_data) >= FILE_CONFIG['max_columns_per_day']:
                                break
            
            self.logger.info(f"Found {len(columns_data)} columns")
            return columns_data
            
        except requests.RequestException as e:
            self.logger.error(f"Request error scraping {url}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error scraping Daily Sabah: {e}")
            return []
    
    def text_to_speech(self, text: str, filename: str) -> Optional[str]:
        """Convert text to speech using OpenAI TTS"""
        try:
            self.logger.info(f"Generating TTS for {filename} (text length: {len(text)})")
            
            response = self.client.audio.speech.create(
                model=TTS_CONFIG['model'],
                voice=TTS_CONFIG['voice'],
                input=text
            )
            
            audio_path = os.path.join(self.output_dir, filename)
            response.stream_to_file(audio_path)
            
            self.logger.info(f"Successfully generated audio: {audio_path}")
            return audio_path
            
        except OpenAIError as e:
            self.logger.error(f"OpenAI API Error for {filename}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"General Error generating TTS for {filename}: {e}")
            return None
    
    def demo_turkish_tts(self) -> Optional[str]:
        """Demo function to test Turkish TTS"""
        self.logger.info("Running Turkish TTS demo...")
        
        # Sample Turkish text
        turkish_text = """
        Merhaba! Bu, Türkçe metin okuma teknolojisinin bir demosu. 
        Yapay zeka teknolojisi sayesinde, yazılı metinleri doğal sesli konuşmaya dönüştürebiliyoruz. 
        Bu teknoloji, haber makalelerini sesli olarak dinlemek için kullanılabilir.
        Günlük haberler artık sesli olarak dinlenebilir.
        """
        
        filename = f"turkish_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{TTS_CONFIG['output_format']}"
        audio_path = self.text_to_speech(turkish_text, filename)
        
        if audio_path:
            self.logger.info(f"✓ Turkish TTS demo successful! Audio saved to: {audio_path}")
            return audio_path
        else:
            self.logger.error("✗ Turkish TTS demo failed")
            return None
    
    def create_safe_filename(self, title: str, index: int, date_str: str) -> str:
        """Create a safe filename from title"""
        # Remove special characters and limit length
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:30]
        
        return FILE_CONFIG['filename_format'].format(
            date=date_str,
            index=index,
            title_short=safe_title,
            ext=TTS_CONFIG['output_format']
        )
    
    def process_daily_columns(self) -> List[Dict]:
        """Main function to process daily columns"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        self.logger.info(f"Processing columns for {date_str}")
        
        columns = self.get_daily_sabah_columns()
        
        if not columns:
            self.logger.warning("No columns found to process. Running TTS demo instead.")
            demo_result = self.demo_turkish_tts()
            return [{'demo': demo_result}] if demo_result else []
        
        processed_files = []
        
        for i, column in enumerate(columns, 1):
            self.logger.info(f"Processing column {i}/{len(columns)}: {column['title'][:50]}...")
            
            # Create filename
            filename = self.create_safe_filename(
                column['title'], 
                i, 
                datetime.now().strftime('%Y%m%d')
            )
            
            # Generate TTS
            audio_path = self.text_to_speech(column['content'], filename)
            
            if audio_path:
                processed_files.append({
                    'title': column['title'],
                    'author': column.get('author', 'Unknown'),
                    'audio_file': audio_path,
                    'original_url': column['url'],
                    'date': column['date'],
                    'file_size': os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
                })
                self.logger.info(f"✓ Generated audio: {filename}")
            else:
                self.logger.error(f"✗ Failed to generate audio for: {column['title']}")
        
        # Save metadata
        metadata_filename = FILE_CONFIG['metadata_format'].format(
            date=datetime.now().strftime('%Y%m%d')
        )
        metadata_file = os.path.join(self.output_dir, metadata_filename)
        
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(processed_files, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Metadata saved to {metadata_file}")
        except Exception as e:
            self.logger.error(f"Error saving metadata: {e}")
        
        self.logger.info(f"Processed {len(processed_files)} columns successfully")
        return processed_files

def main():
    """Main function"""
    app = NewsTTSApp()
    
    if SCHEDULE_CONFIG['enabled']:
        # Schedule daily execution
        schedule.every().day.at(SCHEDULE_CONFIG['time']).do(app.process_daily_columns)
        
        print(f"News TTS App started. Scheduled to run daily at {SCHEDULE_CONFIG['time']}")
        print("Press Ctrl+C to stop")
        
        # Run once immediately for testing
        print("Running initial test...")
        result = app.process_daily_columns()
        
        if result:
            print("✓ Initial test successful!")
        else:
            print("✗ Initial test encountered issues")
        
        # Keep the scheduler running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nApplication stopped by user")
    else:
        # Run once
        print("Running News TTS App once...")
        result = app.process_daily_columns()
        
        if result:
            print("✓ Application completed successfully!")
        else:
            print("✗ Application encountered issues")

if __name__ == "__main__":
    main()

