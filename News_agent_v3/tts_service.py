"""
Text-to-Speech service using Google Gemini API 
"""
import os 
import wave
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

class TTSInference:
    """Text-to-Speech inference using Google Gemini API."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file!")
        
        self.client = genai.Client(api_key=self.api_key)
        print(f"✓ API key loaded: {self.api_key[:5]}...")

    def _save_wave_file(self, filename: str, pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
        """Save PCM data to a WAV file."""
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm_data)
        
    async def generate_audio(
        self,
        text: str,
        voice_name: str = "Sadaltager",
        tone_instructions: str = None,
        model: str = "gemini-2.5-flash-preview-tts",  # ✅ Add model parameter with default
        output_folder: str = None
    ) -> str:
        """
        Generate audio from text using Gemini TTS.
        
        Args:
            text: Text to convert to speech
            voice_name: Voice name (e.g., "Sadaltager", "Aoede", "Charon")
            tone_instructions: Instructions for tone/style
            model: TTS model to use
            output_folder: Folder to save audio (if None, uses default outputs folder)
        
        Returns:
            Path to generated audio file
        """
        try:
            print(f"🎤 Generating speech audio with voice {voice_name} using {model}...")
            
            # Prepare prompt with tone instructions
            full_prompt = text
            if tone_instructions:
                full_prompt = f"{tone_instructions}: {text}"
            
            # Generate audio
            response = self.client.models.generate_content(
                model=model,  # ✅ Use the model parameter
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        )
                    )
                )
            )

            # Extract audio data
            audio_data = response.candidates[0].content.parts[0].inline_data.data

            # Save to file in specified folder
            if output_folder:
                output_path = Path(output_folder) / "audio.wav"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = Path("outputs") / f"audio_{timestamp}.wav"
            
            output_path.parent.mkdir(exist_ok=True, parents=True)
            
            self._save_wave_file(str(output_path), audio_data)

            print(f"✅ Audio saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ TTS generation failed: {e}")
            raise
        
    def get_available_voices(self) -> list:
        """Get list of available voice names."""
        return [
            "Sadaltager",
            "Aoede",
            "Charon", 
            "Fenrir",
            "Kore",
            "Puck"
        ]