# 🎙️ Voice-Activated Virtual Assistant

A modular, robust, Python 3.x voice-activated virtual assistant with continuous wake-word detection, speech recognition (STT), text-to-speech (TTS), email automation, web browsing, information retrieval, safe mathematical expression evaluation, reminders, and local application launcher.

---

## 📁 Project Structure

```
voice-assistant/
├── config.py                 # Central configuration loaded from .env
├── main.py                   # Main entry point & listen-process-respond loop
├── requirements.txt          # Project dependencies
├── .env.example              # Environment configuration template
├── .env                      # Local environment configuration
├── README.md                 # Documentation & setup guide
├── data/
│   ├── contacts.json         # Name-to-email mapping database
│   └── reminders.json        # Reminders persistent storage
├── logs/
│   └── assistant.log         # System & error logs
├── speech/
│   ├── __init__.py
│   ├── listener.py           # Speech recognition & wake-word engine
│   └── speaker.py            # Text-To-Speech (pyttsx3 & gTTS fallback)
├── intents/
│   ├── __init__.py
│   └── intent_matcher.py     # Intent classification & command routing
└── modules/
    ├── __init__.py
    ├── email_handler.py      # SMTP/IMAP email composer & reader
    ├── web_search.py         # Wikipedia, Weather, News & Safe Math Evaluator
    ├── browser_control.py    # Web browsing, Google search, YouTube player
    └── utilities.py          # Date/time, reminders, jokes & local app launcher
```

---

## ⚙️ Prerequisites & Installation

### 1. Python Environment
Ensure you have **Python 3.8+** installed:
```bash
python --version
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install PyAudio (Required for Microphone Input)
- **Windows**:
  ```bash
  pip install pyaudio
  ```
  *If `pip install pyaudio` fails on Windows, install via wheel or pipwin:*
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get install portaudio19-dev python3-pyaudio
  pip install pyaudio
  ```
- **macOS**:
  ```bash
  brew install portaudio
  pip install pyaudio
  ```

### 4. Install Project Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Configuration & API Keys

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to configure your settings:

### 1. Email Credentials Setup (Gmail App Password)
To allow the assistant to send and read emails safely:
1. Go to your **Google Account Security Settings**.
2. Ensure **2-Step Verification** is turned ON.
3. Search for **App passwords**.
4. Generate a new App Password for "Mail" / "Virtual Assistant".
5. Paste the 16-character generated password into `.env`:
   ```env
   EMAIL_ADDRESS="your.email@gmail.com"
   EMAIL_PASSWORD="xxxx xxxx xxxx xxxx"
   ```

### 2. OpenWeatherMap API Key (Weather)
1. Sign up for a free account at [OpenWeatherMap](https://home.openweathermap.org/users/sign_up).
2. Get your API Key from the API Keys tab.
3. Update `.env`:
   ```env
   OPENWEATHER_API_KEY="your_openweather_api_key"
   DEFAULT_CITY="New York"
   ```

### 3. NewsAPI Key (Headlines)
1. Register for a free API Key at [NewsAPI.org](https://newsapi.org/).
2. Update `.env`:
   ```env
   NEWS_API_KEY="your_news_api_key"
   ```

---

## 🚀 Running the Assistant

### Mode A: Full Voice Mode (Microphone Required)
Start the continuous wake-word listener loop:
```bash
python main.py
```
1. Say: `"Hey Assistant"` (or your configured wake word).
2. The assistant will respond: `"Yes? I am listening."`
3. Speak your command (e.g., `"What is the weather in London?"`).

### Mode B: Terminal Text Mode (No Microphone Required)
Ideal for testing without a microphone or in quiet environments:
```bash
python main.py --text
```

---

## 🗣️ Supported Commands Reference

| Intent Category | Spoken Example Commands |
|---|---|
| **Wake Word** | *"Hey Assistant"* |
| **Email** | *"Send email to john saying project update is ready"*<br>*"Read my unread emails"* |
| **Wikipedia** | *"Wikipedia Albert Einstein"*<br>*"Who is Nikola Tesla?"* |
| **Weather** | *"What's the weather in Tokyo?"*<br>*"Tell me the temperature"* |
| **News** | *"Tell me today's news headlines"* |
| **Math** | *"Calculate 45 times 12"*<br>*"What is 150 divided by 3"* |
| **Browsing** | *"Open YouTube"*<br>*"Search Google for python tutorials"* |
| **YouTube** | *"Play Lofi Hip Hop on YouTube"* |
| **System Apps** | *"Open notepad"*<br>*"Launch calculator"* |
| **Reminders** | *"Remind me to buy groceries"*<br>*"Read my reminders"*<br>*"Clear all reminders"* |
| **Date & Time** | *"What time is it?"*<br>*"What is today's date?"* |
| **Jokes & Chat** | *"Tell me a joke"*<br>*"Hello"* |
| **Exit** | *"Stop"* / *"Quit"* / *"Exit"* / *"Goodbye"* |

---

## 🛡️ Security & Best Practices

- **No `eval()`**: All math computations use a safe AST parser (`SafeCalculator` in `modules/web_search.py`) to prevent arbitrary code execution vulnerabilities.
- **Secure Email**: Uses SSL/TLS with App-Specific Passwords instead of plain text account passwords.
- **Environment Isolation**: API keys and passwords are loaded via `python-dotenv` and ignored in `.gitignore`.
