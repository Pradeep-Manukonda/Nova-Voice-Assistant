import logging
import speech_recognition as sr
import config

logger = logging.getLogger(__name__)

class Listener:
    """
    Speech recognition engine handling microphone audio input,
    ambient noise calibration, wake-word detection, and Speech-to-Text conversion.
    """

    def __init__(self, wake_word: str = config.WAKE_WORD, text_mode: bool = False):
        self.wake_word = wake_word.lower()
        self.text_mode = text_mode
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = config.DYNAMIC_ENERGY_THRESHOLD
        self.microphone_available = False

        if not self.text_mode:
            self._check_microphone()

    def _check_microphone(self):
        try:
            mics = sr.Microphone.list_microphone_names()
            if mics:
                self.microphone_available = True
                logger.info(f"Microphone detected. Count: {len(mics)}")
            else:
                logger.warning("No microphone detected. Switching to terminal text mode.")
                self.text_mode = True
        except Exception as e:
            logger.warning(f"Error checking microphone: {e}. Switching to terminal text mode.")
            self.text_mode = True

    def calibrate_ambient_noise(self, duration: int = 1):
        """
        Calibrate recognizer for background ambient noise level.
        """
        if self.text_mode or not self.microphone_available:
            return

        try:
            print("🔊 Calibrating microphone for ambient noise...")
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            logger.info(f"Ambient noise calibration done. Threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            logger.error(f"Ambient noise calibration error: {e}")

    def listen_command(self, timeout: int = config.LISTEN_TIMEOUT, phrase_limit: int = config.PHRASE_TIME_LIMIT) -> str:
        """
        Listen for a user spoken command and convert to text string.
        Falls back to terminal input if in text mode or mic unavailable.
        """
        if self.text_mode or not self.microphone_available:
            try:
                user_input = input("\n🎙️ [You (Text Input)]: ").strip()
                return user_input.lower()
            except (EOFError, KeyboardInterrupt):
                return "exit"

        try:
            with sr.Microphone() as source:
                print("\n🎙️ Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

            print("⚡ Recognizing...")
            text = self.recognizer.recognize_google(audio, language=config.LANGUAGE)
            recognized_text = text.lower().strip()
            print(f"👤 [You]: {recognized_text}")
            logger.info(f"Recognized Speech: {recognized_text}")
            return recognized_text

        except sr.WaitTimeoutError:
            logger.debug("Speech recognition timeout: No speech detected.")
            return ""
        except sr.UnknownValueError:
            logger.info("Speech recognition could not understand audio.")
            return "__unrecognized__"
        except sr.RequestError as e:
            logger.error(f"Speech recognition service request error: {e}")
            return "__network_error__"
        except Exception as e:
            logger.error(f"Unexpected error in speech recognition: {e}")
            return ""

    def listen_for_wakeword(self) -> bool:
        """
        Listen continuously until the wake-word is spoken or user types a command in text mode.
        """
        if self.text_mode or not self.microphone_available:
            # In text mode, prompt once
            user_input = input(f"\nType a command (or say '{self.wake_word}'): ").strip().lower()
            if not user_input:
                return False
            # Check if user typed wake word or direct command
            if self.wake_word in user_input:
                return True
            # Store typed command for immediate handling
            self._last_typed_command = user_input
            return True

        self._last_typed_command = None
        spoken_text = self.listen_command(timeout=config.LISTEN_TIMEOUT, phrase_limit=5)
        if self.wake_word in spoken_text:
            return True
        return False

    def get_last_typed_command(self) -> str:
        cmd = getattr(self, "_last_typed_command", None)
        self._last_typed_command = None
        return cmd or ""
