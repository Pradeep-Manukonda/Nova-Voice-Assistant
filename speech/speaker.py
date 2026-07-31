import os
import sys
import logging
import tempfile
import config

logger = logging.getLogger(__name__)

class Speaker:
    """
    Text-to-Speech engine wrapper supporting pyttsx3 (offline)
    and gTTS (online fallback).
    """

    def __init__(self, engine_type: str = config.TTS_ENGINE, rate: int = config.VOICE_RATE, volume: float = config.VOICE_VOLUME, gender: str = config.VOICE_GENDER):
        self.engine_type = engine_type.lower()
        self.rate = rate
        self.volume = volume
        self.gender = gender
        self.pyttsx3_engine = None
        self._init_pyttsx3()

    def _init_pyttsx3(self):
        try:
            import pyttsx3
            self.pyttsx3_engine = pyttsx3.init()
            self.pyttsx3_engine.setProperty("rate", self.rate)
            self.pyttsx3_engine.setProperty("volume", self.volume)

            # Attempt to set desired voice gender/type
            voices = self.pyttsx3_engine.getProperty("voices")
            if voices:
                selected_voice = None
                for voice in voices:
                    voice_name = (voice.name or "").lower()
                    if self.gender == "female" and ("female" in voice_name or "zira" in voice_name or "hazel" in voice_name):
                        selected_voice = voice.id
                        break
                    elif self.gender == "male" and ("male" in voice_name or "david" in voice_name or "george" in voice_name):
                        selected_voice = voice.id
                        break

                if selected_voice:
                    self.pyttsx3_engine.setProperty("voice", selected_voice)
                else:
                    self.pyttsx3_engine.setProperty("voice", voices[0].id)
        except Exception as e:
            logger.warning(f"pyttsx3 initialization failed: {e}. Falling back to terminal text output.")
            self.pyttsx3_engine = None

    def speak(self, text: str):
        """
        Speak out text using configured TTS engine and print to console.
        """
        if not text:
            return

        print(f"\n🤖 [{config.ASSISTANT_NAME}]: {text}")
        logger.info(f"Assistant Spoke: {text}")

        if self.engine_type == "gtts":
            if self._speak_gtts(text):
                return
            # Fall back to pyttsx3 if gTTS failed
            logger.info("Falling back to pyttsx3 engine.")

        self._speak_pyttsx3(text)

    def _speak_pyttsx3(self, text: str):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            voices = engine.getProperty("voices")
            if voices:
                selected_voice = None
                for voice in voices:
                    voice_name = (voice.name or "").lower()
                    if self.gender == "female" and ("female" in voice_name or "zira" in voice_name or "hazel" in voice_name):
                        selected_voice = voice.id
                        break
                    elif self.gender == "male" and ("male" in voice_name or "david" in voice_name or "george" in voice_name):
                        selected_voice = voice.id
                        break
                if selected_voice:
                    engine.setProperty("voice", selected_voice)
                else:
                    engine.setProperty("voice", voices[0].id)

            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"pyttsx3 speech error: {e}")


    def _speak_gtts(self, text: str) -> bool:
        try:
            from gtts import gTTS
            from playsound import playsound

            tts = gTTS(text=text, lang="en", slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_filename = fp.name

            tts.save(temp_filename)
            playsound(temp_filename)
            os.remove(temp_filename)
            return True
        except Exception as e:
            logger.warning(f"gTTS speech execution failed: {e}")
            return False
