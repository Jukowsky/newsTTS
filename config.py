# Configuration file for Turkish News TTS Application

# News Source Configuration
NEWS_SOURCE = {
    'name': 'Daily Sabah',
    'url': 'https://www.dailysabah.com/columns',
    'selectors': {
        'article_cards': 'div.article-card',
        'title': 'h3',
        'author': 'div.author-info',
        'link': 'a.card',
        'content': [
            'div.article-content',
            'div.content',
            'div.post-content',
            'article',
            'div.entry-content'
        ]
    }
}

# TTS Configuration
TTS_CONFIG = {
    'provider': 'openai',  # Currently only OpenAI is implemented
    'model': 'tts-1',      # Options: 'tts-1', 'tts-1-hd'
    'voice': 'alloy',      # Options: alloy, echo, fable, onyx, nova, shimmer
    'output_format': 'wav'
}

# Scheduling Configuration
SCHEDULE_CONFIG = {
    'enabled': True,
    'time': '09:00',       # 24-hour format
    'timezone': 'local'    # Use local timezone
}

# File Management
FILE_CONFIG = {
    'output_directory': 'audio_files',
    'max_columns_per_day': 5,
    'filename_format': '{date}_{index}_{title_short}.{ext}',
    'metadata_format': 'metadata_{date}.json'
}

# Request Configuration
REQUEST_CONFIG = {
    'timeout': 30,         # seconds
    'retries': 3,
    'delay_between_requests': 1,  # seconds
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',       # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'news_tts.log'
}

