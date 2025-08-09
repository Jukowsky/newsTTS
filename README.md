# Swedish News TTS Generator 🇸🇪🔊

A Python application that scrapes Swedish news articles from [RiktpunKt.nu](https://riktpunkt.nu/) and converts them to high-quality audio using ElevenLabs Text-to-Speech API.

## Features ✨

- 🗞️ **Smart News Scraping**: Extracts full article content with metadata
- 🎤 **High-Quality TTS**: Uses ElevenLabs multilingual voices for natural Swedish speech
- 📁 **Organized Output**: Creates structured files for easy management
- 🎵 **Playlist Generation**: Automatically creates M3U playlists
- ⚡ **Rate Limiting**: Respects API limits and server resources
- 🛡️ **Error Handling**: Robust error handling and diagnostics

## Project Structure 📂

```
swedish-news-tts/
├── news_scraper.py          # Enhanced news scraper
├── tts_generator.py         # ElevenLabs TTS generator
├── api_tester.py           # API diagnostics tool
├── .env                    # Environment variables (create this)
├── articles_for_tts/       # Scraped articles (auto-generated)
├── audio_news/             # Generated audio files (auto-generated)
├── scraped_news.json       # Structured article data
├── scraped_news.txt        # Human-readable articles
└── README.md              # This file
```

## Installation 🚀

### Prerequisites
- Python 3.7+
- ElevenLabs API account
- Internet connection

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/swedish-news-tts.git
   cd swedish-news-tts
   ```

2. **Install dependencies**
   ```bash
   pip install requests beautifulsoup4 pathlib
   ```

3. **Get ElevenLabs API Key**
   - Sign up at [ElevenLabs.io](https://elevenlabs.io)
   - Navigate to your profile → API Keys
   - Create a new API key

4. **Set up environment variables**

   **Option A: Create .env file (Recommended)**
   ```bash
   # Create .env file in project root
   echo "ELEVENLABS_API_KEY=your_actual_api_key_here" > .env
   ```

   **Option B: Set environment variable**
   
   *Windows:*
   ```cmd
   set ELEVENLABS_API_KEY=your_actual_api_key_here
   ```
   
   *macOS/Linux:*
   ```bash
   export ELEVENLABS_API_KEY="your_actual_api_key_here"
   ```

## Usage 📖

### Step 1: Scrape News Articles
```bash
python news_scraper.py
```

This will:
- Fetch latest articles from RiktpunKt.nu
- Extract full article content and metadata
- Save articles in multiple formats
- Create individual text files for TTS processing

### Step 2: Test API Connection (Optional)
```bash
python api_tester.py
```

This diagnostic tool will:
- Validate your API key
- Show available voices
- Test TTS generation
- Help troubleshoot issues

### Step 3: Generate Audio Files
```bash
python tts_generator.py
```

This will:
- Process all scraped articles
- Convert text to Swedish speech
- Save high-quality MP3 files
- Create a playlist for continuous listening

## Output Files 📄

### News Scraper Output
- `scraped_news.json` - Structured article data with metadata
- `scraped_news.txt` - Human-readable format
- `articles_for_tts/` - Individual text files ready for TTS

### TTS Generator Output
- `audio_news/` - MP3 audio files
- `news_playlist.m3u` - Playlist for media players
- Long articles are automatically split into multiple parts

## Configuration ⚙️

### Environment Variables
```bash
ELEVENLABS_API_KEY=your_api_key_here    # Required
MAX_ARTICLES=10                         # Optional: Limit articles to process
VOICE_STABILITY=0.5                     # Optional: TTS voice stability
AUDIO_OUTPUT_FOLDER=audio_news          # Optional: Custom output folder
```

### Customization Options

**In `news_scraper.py`:**
- Change `article_urls[:10]` to process more/fewer articles
- Modify delay with `time.sleep(1)` for different scraping speed

**In `tts_generator.py`:**
- Adjust `max_length=5000` for different text chunk sizes
- Modify voice settings in the `voice_settings` object
- Change `time.sleep(2)` for different API rate limiting

## API Costs 💰

ElevenLabs charges per character converted:
- Free tier: 10,000 characters/month
- Paid plans: Starting at $5/month for 30,000 characters

**Cost estimation for typical news articles:**
- Average article: ~2,000 characters
- 5 articles ≈ 10,000 characters (free tier limit)
- 15 articles ≈ $5 worth of usage

## Troubleshooting 🔧

### Common Issues

**401 Unauthorized Error:**
```bash
# Test your API key
python api_tester.py

# Common solutions:
# 1. Generate new API key from ElevenLabs dashboard
# 2. Check .env file formatting
# 3. Verify account has remaining credits
```

**No Articles Found:**
```bash
# Check website accessibility
curl -I https://riktpunkt.nu/

# Verify scraper is working
python news_scraper.py
```

**Poor Audio Quality:**
- Try different voices with the voice selection menu
- Adjust `stability` and `similarity_boost` settings
- Use `eleven_multilingual_v2` model for Swedish

### Debug Mode
Add debug prints to see what's happening:
```python
# In any script, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Areas for Improvement
- Support for additional news sources
- Voice cloning for specific speakers
- Batch processing optimization
- GUI interface
- Docker containerization


## Acknowledgments 🙏

- [RiktpunKt.nu](https://riktpunkt.nu/) for providing news content
- [ElevenLabs](https://elevenlabs.io) for high-quality TTS API
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for web scraping
- Swedish language community for feedback and testing

## Support 💬

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting-) section
2. Run the diagnostic script: `python api_tester.py`
3. Open an issue with:
   - Error messages
   - Python version
   - Operating system
   - Steps to reproduce

---
