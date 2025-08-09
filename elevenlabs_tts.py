import os
import json
import requests
import time
from pathlib import Path
import re
from typing import List, Dict, Optional

class ElevenLabsSwedishTTS:
    def __init__(self, api_key: str):
        """
        Initialize the ElevenLabs TTS client
        
        Args:
            api_key: Your ElevenLabs API key
        """
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Swedish voice IDs (you may need to update these based on available voices)
        # These are example voice IDs - check your ElevenLabs dashboard for actual Swedish voices
        self.swedish_voices = {
            "female_1": "21m00Tcm4TlvDq8ikWAM",  # Example ID - replace with actual Swedish voice
            "male_1": "AZnzlk1XvdvUeBnXmlld",    # Example ID - replace with actual Swedish voice
            "female_2": "EXAVITQu4vr4xnSDxMaL"   # Example ID - replace with actual Swedish voice
        }
        
        self.default_voice = "female_1"
    
    def get_available_voices(self) -> List[Dict]:
        """Get list of available voices from ElevenLabs"""
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            voices_data = response.json()
            swedish_voices = []
            
            # Filter for Swedish voices or voices that work well with Swedish
            for voice in voices_data.get("voices", []):
                # Check if voice supports Swedish or is multilingual
                if any("swedish" in lang.lower() or "multilingual" in lang.lower() 
                       for lang in voice.get("labels", {}).values()):
                    swedish_voices.append({
                        "voice_id": voice["voice_id"],
                        "name": voice["name"],
                        "category": voice.get("category", ""),
                        "labels": voice.get("labels", {})
                    })
            
            return swedish_voices
            
        except Exception as e:
            print(f"Error fetching voices: {e}")
            return []
    
    def text_to_speech(self, text: str, voice_id: str = None, output_file: str = None) -> bool:
        """
        Convert text to speech using ElevenLabs API
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (uses default if None)
            output_file: Output file path
            
        Returns:
            bool: Success status
        """
        try:
            if voice_id is None:
                voice_id = self.swedish_voices[self.default_voice]
            
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Best model for non-English languages
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            
            # Save audio file
            if output_file:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"✓ Audio saved: {output_file}")
                return True
                
        except requests.exceptions.RequestException as e:
            print(f"✗ API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
        except Exception as e:
            print(f"✗ Error generating TTS: {e}")
            
        return False
    
    def process_news_articles(self, articles_folder: str = "articles_for_tts", 
                            output_folder: str = "audio_news", 
                            voice_id: str = None,
                            max_length: int = 5000) -> None:
        """
        Process all news articles from the scraper and generate TTS
        
        Args:
            articles_folder: Folder containing text articles
            output_folder: Folder to save audio files
            voice_id: Voice ID to use
            max_length: Maximum text length per audio file (to avoid API limits)
        """
        
        # Create output directory
        os.makedirs(output_folder, exist_ok=True)
        
        # Get all text files from articles folder
        articles_path = Path(articles_folder)
        if not articles_path.exists():
            print(f"Articles folder '{articles_folder}' not found!")
            print("Please run the news scraper first.")
            return
        
        text_files = list(articles_path.glob("*.txt"))
        
        if not text_files:
            print(f"No text files found in '{articles_folder}'")
            return
        
        print(f"Found {len(text_files)} articles to process")
        
        successful = 0
        failed = 0
        
        for i, text_file in enumerate(text_files, 1):
            try:
                print(f"\nProcessing {i}/{len(text_files)}: {text_file.name}")
                
                # Read article content
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if not content:
                    print(f"✗ Empty file: {text_file.name}")
                    failed += 1
                    continue
                
                # Split content if it's too long
                if len(content) > max_length:
                    print(f"⚠ Article too long ({len(content)} chars), splitting...")
                    parts = self.split_text(content, max_length)
                    
                    for part_idx, part in enumerate(parts):
                        audio_filename = f"{text_file.stem}_part{part_idx + 1:02d}.mp3"
                        audio_path = os.path.join(output_folder, audio_filename)
                        
                        success = self.text_to_speech(part, voice_id, audio_path)
                        if success:
                            successful += 1
                        else:
                            failed += 1
                        
                        # Rate limiting - be respectful to the API
                        time.sleep(2)
                else:
                    # Generate single audio file
                    audio_filename = f"{text_file.stem}.mp3"
                    audio_path = os.path.join(output_folder, audio_filename)
                    
                    success = self.text_to_speech(content, voice_id, audio_path)
                    if success:
                        successful += 1
                    else:
                        failed += 1
                    
                    # Rate limiting
                    time.sleep(2)
                    
            except Exception as e:
                print(f"✗ Error processing {text_file.name}: {e}")
                failed += 1
                continue
        
        print(f"\n{'='*50}")
        print(f"TTS Generation Complete!")
        print(f"✓ Successful: {successful}")
        print(f"✗ Failed: {failed}")
        print(f"Audio files saved in: {output_folder}")
    
    def split_text(self, text: str, max_length: int) -> List[str]:
        """
        Split text into chunks that respect sentence boundaries
        
        Args:
            text: Text to split
            max_length: Maximum length per chunk
            
        Returns:
            List of text chunks
        """
        # Split by sentences (Swedish sentence endings)
        sentences = re.split(r'[.!?]+\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence would exceed max_length, start new chunk
            if len(current_chunk) + len(sentence) + 2 > max_length and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += ". " + sentence if current_chunk else sentence
        
        # Add remaining chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def create_playlist(self, audio_folder: str = "audio_news") -> None:
        """Create an M3U playlist of all generated audio files"""
        
        audio_path = Path(audio_folder)
        if not audio_path.exists():
            print(f"Audio folder '{audio_folder}' not found!")
            return
        
        audio_files = sorted(list(audio_path.glob("*.mp3")))
        
        if not audio_files:
            print(f"No audio files found in '{audio_folder}'")
            return
        
        playlist_path = audio_path / "news_playlist.m3u"
        
        with open(playlist_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for audio_file in audio_files:
                f.write(f"#EXTINF:-1,{audio_file.stem}\n")
                f.write(f"{audio_file.name}\n")
        
        print(f"✓ Playlist created: {playlist_path}")


def main():
    """Main function to run the TTS generator"""
    
    # Get API key from environment variable or user input
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("ElevenLabs API Key not found in environment variables.")
        api_key = input("Please enter your ElevenLabs API key: ").strip()
    
    if not api_key:
        print("API key is required. Exiting...")
        return
    
    # Initialize TTS client
    tts = ElevenLabsSwedishTTS(api_key)
    
    print("ElevenLabs Swedish TTS Generator")
    print("=" * 40)
    
    # Get available voices
    print("Fetching available voices...")
    voices = tts.get_available_voices()
    
    if voices:
        print("\nAvailable Swedish/Multilingual voices:")
        for i, voice in enumerate(voices[:5]):  # Show first 5
            print(f"{i+1}. {voice['name']} (ID: {voice['voice_id']})")
        
        # Let user choose voice
        try:
            choice = input(f"\nChoose voice (1-{len(voices)}) or press Enter for default: ").strip()
            if choice and choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(voices):
                    selected_voice = voices[choice_idx]['voice_id']
                else:
                    selected_voice = None
            else:
                selected_voice = None
        except:
            selected_voice = None
    else:
        print("Could not fetch voices. Using default...")
        selected_voice = None
    
    # Process articles
    print(f"\nProcessing news articles...")
    tts.process_news_articles(voice_id=selected_voice)
    
    # Create playlist
    print(f"\nCreating playlist...")
    tts.create_playlist()
    
    print(f"\n✓ All done! Check the 'audio_news' folder for your Swedish news audio files.")


if __name__ == "__main__":
    main()