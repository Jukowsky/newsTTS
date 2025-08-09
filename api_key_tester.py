import os
import requests
import json

def test_elevenlabs_api():
    """Test ElevenLabs API connection and authentication"""
    
    # Get API key
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("❌ ELEVENLABS_API_KEY environment variable not found")
        api_key = input("Enter your ElevenLabs API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    print(f"🔑 Using API key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
    
    # Test 1: Check API key validity with user info
    print("\n📋 Test 1: Checking API key validity...")
    try:
        url = "https://api.elevenlabs.io/v1/user"
        headers = {"xi-api-key": api_key}
        
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ API key is valid!")
            print(f"User ID: {user_info.get('user_id', 'N/A')}")
            print(f"Characters remaining: {user_info.get('subscription', {}).get('character_count', 'N/A')}")
            print(f"Character limit: {user_info.get('subscription', {}).get('character_limit', 'N/A')}")
        else:
            print(f"❌ API key validation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False
    
    # Test 2: Get available voices
    print("\n🎤 Test 2: Getting available voices...")
    try:
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": api_key}
        
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            voices_data = response.json()
            voices = voices_data.get("voices", [])
            print(f"✅ Found {len(voices)} voices")
            
            # Show first few voices
            print("\nAvailable voices:")
            for i, voice in enumerate(voices[:5]):
                labels = voice.get("labels", {})
                accent = labels.get("accent", "N/A")
                age = labels.get("age", "N/A")
                gender = labels.get("gender", "N/A")
                print(f"  {i+1}. {voice['name']} (ID: {voice['voice_id']}) - {gender}, {age}, {accent}")
            
            return voices
        else:
            print(f"❌ Failed to get voices: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting voices: {e}")
        return False

def test_tts_with_voice(api_key: str, voice_id: str):
    """Test TTS generation with a specific voice"""
    
    print(f"\n🔊 Test 3: Testing TTS with voice {voice_id}...")
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": "Hej! Detta är ett test av svensk text-till-tal.",
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ TTS generation successful!")
            
            # Save test audio
            with open("test_audio.mp3", "wb") as f:
                f.write(response.content)
            print("💾 Test audio saved as 'test_audio.mp3'")
            return True
        else:
            print(f"❌ TTS generation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing TTS: {e}")
        return False

if __name__ == "__main__":
    print("ElevenLabs API Diagnostics")
    print("=" * 40)
    
    voices = test_elevenlabs_api()
    
    if voices:
        print(f"\n🎯 Testing TTS generation...")
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            api_key = input("Enter your ElevenLabs API key: ").strip()
        
        # Use the first available voice for testing
        test_voice_id = voices[0]['voice_id']
        test_tts_with_voice(api_key, test_voice_id)
    
    print(f"\n{'='*40}")
    print("Diagnostic complete!")