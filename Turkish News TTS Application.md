# Turkish News TTS Application

A Python application that automatically scrapes Turkish news columns from Daily Sabah and converts them to audio files using OpenAI's Text-to-Speech API.

## Features

- **Daily News Scraping**: Automatically fetches the latest columns from Daily Sabah
- **Turkish TTS Support**: Uses OpenAI's TTS API which supports Turkish language
- **Scheduled Execution**: Runs daily at a specified time (default: 9:00 AM)
- **Audio File Management**: Saves audio files with organized naming and metadata
- **Error Handling**: Robust error handling for network issues and API failures
- **Configurable**: Easy to modify for different news sources or TTS providers

## Prerequisites

1. **Python 3.7+**
2. **OpenAI API Key**: You need a valid OpenAI API key with access to the TTS endpoint
3. **Internet Connection**: Required for web scraping and API calls

## Installation

1. **Clone or download the application files**

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   
   **Option A: Environment Variable (Recommended)**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```
   
   **Option B: Modify the code**
   Edit `news_tts_app.py` and replace:
   ```python
   self.client = openai.OpenAI()
   ```
   with:
   ```python
   self.client = openai.OpenAI(api_key="your-openai-api-key-here")
   ```

## Usage

### Basic Usage

Run the application once:
```bash
python3 news_tts_app.py
```

This will:
1. Scrape the latest columns from Daily Sabah
2. Convert each column to audio using Turkish TTS
3. Save audio files in the `audio_files/` directory
4. Generate a metadata JSON file with details

### Scheduled Execution

To run the application daily at 9:00 AM, uncomment the scheduling code in `main()`:

```python
def main():
    app = NewsTTSApp()
    
    # Schedule daily execution at 9:00 AM
    schedule.every().day.at("09:00").do(app.process_daily_columns)
    
    print("News TTS App started. Scheduled to run daily at 9:00 AM")
    print("Press Ctrl+C to stop")
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
```

### Running as a Service

For production use, you can run this as a system service:

**Create a systemd service file** (`/etc/systemd/system/news-tts.service`):
```ini
[Unit]
Description=Turkish News TTS Application
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/your/app
Environment=OPENAI_API_KEY=your-api-key-here
ExecStart=/usr/bin/python3 /path/to/your/app/news_tts_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start the service**:
```bash
sudo systemctl enable news-tts.service
sudo systemctl start news-tts.service
```

## Configuration

### Changing the News Source

To use a different Turkish news website, modify the `get_daily_sabah_columns()` method:

1. Update the URL
2. Adjust the HTML selectors for the new site's structure
3. Modify the content extraction logic if needed

### Changing TTS Settings

You can modify the TTS settings in the `text_to_speech()` method:

```python
response = self.client.audio.speech.create(
    model="tts-1",  # or "tts-1-hd" for higher quality
    voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
    input=text
)
```

### Changing Schedule Time

Modify the schedule time in the `main()` function:
```python
schedule.every().day.at("09:00").do(app.process_daily_columns)  # 9:00 AM
schedule.every().day.at("18:30").do(app.process_daily_columns)  # 6:30 PM
```

## Output Structure

The application creates the following structure:

```
audio_files/
├── 20250723_1_Syria_stability_unity_and_fut.wav
├── 20250723_2_How_to_motivate_a_generation_t.wav
├── 20250723_3_A_festival_of_liberation_for_T.wav
└── metadata_20250723.json
```

### Metadata Format

The metadata JSON file contains:
```json
[
  {
    "title": "Syria's stability, unity and future are under Israeli siege",
    "audio_file": "audio_files/20250723_1_Syria_stability_unity_and_fut.wav",
    "original_url": "https://www.dailysabah.com/columns/...",
    "date": "2025-07-23"
  }
]
```

## Troubleshooting

### Common Issues

1. **OpenAI API 404 Error**
   - Ensure your API key is valid and has TTS access
   - Check if you have sufficient API credits
   - Verify the API key is properly set as an environment variable

2. **No Columns Found**
   - The website structure may have changed
   - Check your internet connection
   - The site may be blocking automated requests

3. **Audio Files Not Generated**
   - Check the `audio_files/` directory permissions
   - Ensure sufficient disk space
   - Review the console output for specific error messages

### Debug Mode

Add debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Alternative TTS Providers

If you prefer to use a different TTS provider, you can modify the `text_to_speech()` method. Popular alternatives include:

- **ElevenLabs**: High-quality voices with Turkish support
- **Google Cloud TTS**: Good Turkish support
- **Azure Cognitive Services**: Microsoft's TTS with Turkish voices
- **Amazon Polly**: AWS TTS service

## Legal Considerations

- Ensure you comply with the website's robots.txt and terms of service
- Respect rate limits to avoid being blocked
- Consider the copyright implications of converting news content to audio
- This tool is for personal/educational use

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is provided as-is for educational and personal use.

