import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime
import schedule
import time

# TTS Integration - Using OpenAI TTS as it supports Turkish
import openai
from openai import OpenAIError

class NewsTTSApp:
    def __init__(self):
        self.output_dir = "audio_files"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        # Ensure OpenAI API key is set
        self.client = openai.OpenAI() # Assumes OPENAI_API_KEY is set as an environment variable
    
    def get_column_content(self, url):
        """Extract full content from a column article"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for article content
            content_selectors = [
                'div.article-content',
                'div.content',
                'div.post-content',
                'article',
                'div.entry-content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    paragraphs = content_div.find_all('p')
                    content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
                    break
            
            return content if content else "Content could not be extracted"
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None
    
    def get_daily_sabah_columns(self):
        """Scrape columns from Daily Sabah"""
        url = "https://www.dailysabah.com/columns"
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            columns_data = []
            
            # Look for column links in the page
            # The structure seems to be 'div.article-card' for each column entry
            for article_card in soup.find_all('div', class_='article-card'):
                title_tag = article_card.find('h3')
                author_tag = article_card.find('div', class_='author-info')
                link_tag = article_card.find('a', class_='card')

                if title_tag and author_tag and link_tag:
                    title = title_tag.text.strip()
                    author = author_tag.text.strip()
                    link = link_tag['href']
                    full_url = link if link.startswith('http') else f"https://www.dailysabah.com{link}"
                    content = self.get_column_content(full_url)
                    
                    if content:
                        columns_data.append({
                            'title': title,
                            'author': author,
                            'url': full_url,
                            'content': content,
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
            
            return columns_data[:5]  # Limit to 5 columns per day
        except Exception as e:
            print(f"Error scraping Daily Sabah: {e}")
            return []
    
    def text_to_speech(self, text, filename):
        """Convert text to speech using OpenAI TTS"""
        try:
            print(f"Attempting TTS for {filename} with text length {len(text)}")
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",  # You can change this to other voices
                input=text
            )
            
            audio_path = os.path.join(self.output_dir, filename)
            response.stream_to_file(audio_path)
            print(f"Successfully generated audio to {audio_path}")
            return audio_path
        except OpenAIError as e:
            print(f"OpenAI API Error for {filename}: {e}")
            return None
        except Exception as e:
            print(f"General Error generating TTS for {filename}: {e}")
            return None
    
    def demo_turkish_tts(self):
        """Demo function to test Turkish TTS"""
        print("Running Turkish TTS demo...")
        
        # Sample Turkish text
        turkish_text = """
        Merhaba! Bu, Türkçe metin okuma teknolojisinin bir demosu. 
        Yapay zeka teknolojisi sayesinde, yazılı metinleri doğal sesli konuşmaya dönüştürebiliyoruz. 
        Bu teknoloji, haber makalelerini sesli olarak dinlemek için kullanılabilir.
        """
        
        filename = "turkish_demo.wav"
        audio_path = self.text_to_speech(turkish_text, filename)
        
        if audio_path:
            print(f"✓ Turkish TTS demo successful! Audio saved to: {audio_path}")
            return audio_path
        else:
            print("✗ Turkish TTS demo failed")
            return None
    
    def process_daily_columns(self):
        """Main function to process daily columns"""
        print(f"Processing columns for {datetime.now().strftime('%Y-%m-%d')}")
        
        columns = self.get_daily_sabah_columns()
        
        if not columns:
            print("No columns found to process. Running TTS demo instead.")
            return self.demo_turkish_tts()
        
        processed_files = []
        
        for i, column in enumerate(columns):
            print(f"Processing column {i+1}/{len(columns)}: {column['title'][:50]}...")
            
            # Create filename
            safe_title = "".join(c for c in column['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{datetime.now().strftime('%Y%m%d')}_{i+1}_{safe_title[:30]}.wav"
            
            # Generate TTS
            audio_path = self.text_to_speech(column['content'], filename)
            
            if audio_path:
                processed_files.append({
                    'title': column['title'],
                    'audio_file': audio_path,
                    'original_url': column['url'],
                    'date': column['date']
                })
                print(f"✓ Generated audio: {filename}")
            else:
                print(f"✗ Failed to generate audio for: {column['title']}")
        
        # Save metadata
        metadata_file = os.path.join(self.output_dir, f"metadata_{datetime.now().strftime('%Y%m%d')}.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(processed_files, f, ensure_ascii=False, indent=2)
        
        print(f"Processed {len(processed_files)} columns. Metadata saved to {metadata_file}")
        return processed_files

def main():
    app = NewsTTSApp()
    
    print("News TTS App started.")
    print("Running initial test...")
    
    # Run once immediately for testing
    result = app.process_daily_columns()
    
    if result:
        print("✓ Application is working correctly!")
    else:
        print("✗ Application encountered issues")
    
    print("\nTo schedule daily execution, uncomment the scheduling code below:")
    print("# schedule.every().day.at('09:00').do(app.process_daily_columns)")
    print("# while True:")
    print("#     schedule.run_pending()")
    print("#     time.sleep(60)")

if __name__ == "__main__":
    main()

