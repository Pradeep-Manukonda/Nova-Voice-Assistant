import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / ".env")

# Assistant Settings
WAKE_WORD = os.getenv("WAKE_WORD", "hey assistant").lower()
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Nova")
LANGUAGE = os.getenv("LANGUAGE", "en-US")

# Speech Synthesis (TTS) Settings
TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3").lower()  # pyttsx3 or gtts
VOICE_RATE = int(os.getenv("VOICE_RATE", "175"))
VOICE_VOLUME = float(os.getenv("VOICE_VOLUME", "1.0"))
VOICE_GENDER = os.getenv("VOICE_GENDER", "female").lower()  # male or female

# Speech Recognition (STT) Settings
STT_ENGINE = os.getenv("STT_ENGINE", "google").lower()  # google or vosk
ENERGY_THRESHOLD = int(os.getenv("ENERGY_THRESHOLD", "4000"))
DYNAMIC_ENERGY_THRESHOLD = os.getenv("DYNAMIC_ENERGY_THRESHOLD", "True").lower() == "true"
LISTEN_TIMEOUT = int(os.getenv("LISTEN_TIMEOUT", "5"))
PHRASE_TIME_LIMIT = int(os.getenv("PHRASE_TIME_LIMIT", "10"))

# Email Credentials
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # App-specific password

# API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "New York")

# Data File Paths
DATA_DIR = BASE_DIR / "data"
CONTACTS_FILE = DATA_DIR / "contacts.json"
REMINDERS_FILE = DATA_DIR / "reminders.json"

# Logging Settings
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "assistant.log"

# Ensure required directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
