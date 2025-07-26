# Deployment Guide - Turkish News TTS Application

This guide covers different deployment options for the Turkish News TTS application.

## Quick Start

1. **Download the application files**
2. **Set your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```
3. **Run the application**:
   ```bash
   ./run.sh
   ```

## Deployment Options

### 1. Local Development

**Requirements:**
- Python 3.7+
- OpenAI API key
- Internet connection

**Steps:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-key-here"

# Run the application
python3 news_tts_app_enhanced.py
```

### 2. Systemd Service (Linux)

**Create service file** (`/etc/systemd/system/news-tts.service`):
```ini
[Unit]
Description=Turkish News TTS Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/news-tts
Environment=OPENAI_API_KEY=your-api-key-here
ExecStart=/usr/bin/python3 /home/ubuntu/news-tts/news_tts_app_enhanced.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable news-tts.service
sudo systemctl start news-tts.service
sudo systemctl status news-tts.service
```

### 3. Docker Deployment

**Build and run:**
```bash
cd docker
cp .env.example .env
# Edit .env with your API key
docker-compose up -d
```

**Check logs:**
```bash
docker-compose logs -f news-tts
```

### 4. Cron Job (Simple Scheduling)

**Add to crontab:**
```bash
crontab -e
```

**Add line for daily execution at 9 AM:**
```
0 9 * * * cd /path/to/news-tts && /usr/bin/python3 news_tts_app_enhanced.py >> logs/cron.log 2>&1
```

### 5. Cloud Deployment

#### AWS EC2

1. **Launch EC2 instance** (Ubuntu 20.04+)
2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
3. **Upload application files**
4. **Set up systemd service** (see above)
5. **Configure security group** (if adding web interface)

#### Google Cloud Platform

1. **Create Compute Engine instance**
2. **Follow local deployment steps**
3. **Set up firewall rules** if needed

#### Azure VM

1. **Create Virtual Machine** (Ubuntu)
2. **Install Python and dependencies**
3. **Deploy application**
4. **Configure Network Security Group**

### 6. Kubernetes Deployment

**Create namespace:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: news-tts
```

**Create secret for API key:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openai-secret
  namespace: news-tts
type: Opaque
stringData:
  OPENAI_API_KEY: "your-api-key-here"
```

**Create deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: news-tts-app
  namespace: news-tts
spec:
  replicas: 1
  selector:
    matchLabels:
      app: news-tts
  template:
    metadata:
      labels:
        app: news-tts
    spec:
      containers:
      - name: news-tts
        image: your-registry/news-tts:latest
        envFrom:
        - secretRef:
            name: openai-secret
        volumeMounts:
        - name: audio-storage
          mountPath: /app/audio_files
      volumes:
      - name: audio-storage
        persistentVolumeClaim:
          claimName: audio-pvc
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `TZ` | Timezone (e.g., Europe/Istanbul) | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |

### Configuration File

Edit `config.py` to customize:

- **News source URL and selectors**
- **TTS settings** (model, voice, format)
- **Scheduling** (time, timezone)
- **File management** (output directory, naming)
- **Request settings** (timeout, retries)

## Monitoring and Maintenance

### Log Files

- **Application logs**: `logs/news_tts.log`
- **System logs**: `journalctl -u news-tts.service`
- **Docker logs**: `docker-compose logs news-tts`

### Health Checks

**Check if service is running:**
```bash
# Systemd
sudo systemctl status news-tts

# Docker
docker-compose ps

# Process
ps aux | grep news_tts
```

**Check recent audio files:**
```bash
ls -la audio_files/
```

**Check logs for errors:**
```bash
tail -f logs/news_tts.log
grep ERROR logs/news_tts.log
```

### Backup Strategy

**Important files to backup:**
- `audio_files/` - Generated audio files
- `logs/` - Application logs
- `config.py` - Configuration
- `.env` - Environment variables

**Backup script example:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "backup_news_tts_$DATE.tar.gz" audio_files/ logs/ config.py
```

## Troubleshooting

### Common Issues

1. **OpenAI API 404 Error**
   - Check API key validity
   - Verify API credits/billing
   - Ensure TTS endpoint access

2. **No columns found**
   - Website structure may have changed
   - Check internet connectivity
   - Review scraping selectors in config

3. **Permission denied**
   - Check file/directory permissions
   - Ensure user has write access to audio_files/

4. **Service won't start**
   - Check systemd service file syntax
   - Verify file paths in service file
   - Check user permissions

### Debug Mode

**Enable debug logging:**
```python
# In config.py
LOGGING_CONFIG = {
    'level': 'DEBUG',
    # ...
}
```

**Run with verbose output:**
```bash
python3 -u news_tts_app_enhanced.py
```

## Security Considerations

1. **API Key Protection**
   - Never commit API keys to version control
   - Use environment variables or secure vaults
   - Rotate keys regularly

2. **File Permissions**
   - Restrict access to audio files if sensitive
   - Use appropriate user permissions

3. **Network Security**
   - Use HTTPS for all API calls
   - Consider VPN for cloud deployments
   - Implement rate limiting if exposing web interface

4. **Updates**
   - Keep dependencies updated
   - Monitor for security vulnerabilities
   - Test updates in staging environment

## Performance Optimization

1. **Concurrent Processing**
   - Process multiple articles in parallel
   - Use async/await for I/O operations

2. **Caching**
   - Cache article content to avoid re-scraping
   - Store processed articles database

3. **Resource Management**
   - Monitor disk space for audio files
   - Implement cleanup for old files
   - Set memory limits for containers

## Scaling

1. **Horizontal Scaling**
   - Run multiple instances with load balancer
   - Use message queue for job distribution

2. **Storage Scaling**
   - Use cloud storage (S3, GCS, Azure Blob)
   - Implement CDN for audio file delivery

3. **Database Integration**
   - Store metadata in database
   - Track processing history
   - Implement user management

