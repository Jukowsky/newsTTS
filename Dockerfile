# Dockerfile for Turkish News TTS Application

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY news_tts_app_enhanced.py .
COPY config.py .
COPY alternative_tts_providers.py .

# Create audio files directory
RUN mkdir -p audio_files

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OPENAI_API_KEY=""

# Expose port (if you add a web interface later)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "news_tts_app_enhanced.py"]

