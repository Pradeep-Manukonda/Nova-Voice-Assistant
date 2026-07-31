import sys
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

import config
from speech import Speaker
from modules import EmailHandler, WebSearchHandler, BrowserController, UtilitiesHandler
from intents import IntentMatcher

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')

app = Flask(__name__)

# Initialize assistant components
speaker = Speaker()
email_handler = EmailHandler()
web_search = WebSearchHandler()
browser_control = BrowserController()
utilities = UtilitiesHandler()

intent_matcher = IntentMatcher(
    email_handler=email_handler,
    web_search=web_search,
    browser_control=browser_control,
    utilities=utilities
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Nova Voice Assistant - Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --border-color: rgba(255, 255, 255, 0.1);
            --primary-accent: #6366f1;
            --primary-hover: #4f46e5;
            --cyan-glow: #06b6d4;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }

        body {
            background: linear-gradient(135deg, #0b0f19 0%, #1e1b4b 50%, #0f172a 100%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem 1rem;
        }

        .container {
            width: 100%;
            max-width: 900px;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        /* Header */
        .header-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 1.25rem;
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        }

        .brand-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .bot-avatar {
            width: 52px;
            height: 52px;
            background: linear-gradient(135deg, #6366f1, #06b6d4);
            border-radius: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.75rem;
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
        }

        .title-group h1 {
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(to right, #ffffff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .title-group p {
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        .status-badge {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(52, 211, 153, 0.3);
            padding: 0.4rem 0.9rem;
            border-radius: 2rem;
            font-size: 0.8rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #34d399;
            border-radius: 50%;
            box-shadow: 0 0 8px #34d399;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.85); }
        }

        /* Conversation Area */
        .chat-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 1.25rem;
            height: 480px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        }

        .chat-logs {
            flex: 1;
            padding: 1.5rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .chat-bubble {
            max-width: 80%;
            padding: 1rem 1.25rem;
            border-radius: 1rem;
            font-size: 0.95rem;
            line-height: 1.5;
            animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .chat-bubble.assistant {
            align-self: flex-start;
            background: rgba(30, 41, 59, 0.9);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #f1f5f9;
            border-top-left-radius: 0.25rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .chat-bubble.user {
            align-self: flex-end;
            background: linear-gradient(135deg, var(--primary-accent), var(--primary-hover));
            color: #ffffff;
            border-top-right-radius: 0.25rem;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        .intent-badge {
            display: inline-block;
            margin-top: 0.4rem;
            font-size: 0.725rem;
            font-weight: 600;
            padding: 0.15rem 0.5rem;
            border-radius: 0.4rem;
            background: rgba(255, 255, 255, 0.1);
            color: var(--cyan-glow);
            text-transform: uppercase;
        }

        /* Controls Section */
        .controls-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 1.25rem;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .input-row {
            display: flex;
            gap: 0.75rem;
        }

        .cmd-input {
            flex: 1;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--border-color);
            border-radius: 0.85rem;
            padding: 0.85rem 1.25rem;
            color: #ffffff;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
        }

        .cmd-input:focus {
            border-color: var(--primary-accent);
            box-shadow: 0 0 12px rgba(99, 102, 241, 0.4);
        }

        .btn {
            background: linear-gradient(135deg, var(--primary-accent), var(--primary-hover));
            color: white;
            border: none;
            border-radius: 0.85rem;
            padding: 0.85rem 1.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }

        .btn-mic {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #f87171;
            width: 48px;
            padding: 0;
        }

        .btn-mic.listening {
            background: #ef4444;
            color: white;
            animation: pulse-red 1.5s infinite;
        }

        @keyframes pulse-red {
            0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            50% { box-shadow: 0 0 0 12px rgba(239, 68, 68, 0); }
        }

        /* Quick Pills */
        .pills-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .pill {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            border-radius: 2rem;
            padding: 0.4rem 0.85rem;
            font-size: 0.8rem;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .pill:hover {
            background: rgba(99, 102, 241, 0.2);
            color: #ffffff;
            border-color: rgba(99, 102, 241, 0.4);
        }

        .tts-toggle {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        .tts-toggle input {
            accent-color: var(--primary-accent);
            cursor: pointer;
        }
    </style>
</head>
<body>

<div class="container">
    <!-- Header -->
    <div class="header-card">
        <div class="brand-info">
            <div class="bot-avatar">🤖</div>
            <div class="title-group">
                <h1>Nova Voice Assistant</h1>
                <p>Real-Time NLU & Voice Virtual Assistant Engine</p>
            </div>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            <span>Localhost Ready</span>
        </div>
    </div>

    <!-- Chat Logs -->
    <div class="chat-card">
        <div class="chat-logs" id="chatLogs">
            <div class="chat-bubble assistant">
                👋 Hello! I am <strong>Nova</strong>, your voice-activated virtual assistant.<br>
                Click the microphone button to speak, or type a command below!
            </div>
        </div>
    </div>

    <!-- Controls -->
    <div class="controls-card">
        <div class="input-row">
            <button class="btn btn-mic" id="micBtn" title="Speak via Browser Microphone">🎙️</button>
            <input type="text" class="cmd-input" id="cmdInput" placeholder="Type a command (e.g. 'What is the time?', 'Tell me a joke')..." onkeydown="if(event.key==='Enter') sendCommand()">
            <button class="btn" onclick="sendCommand()">Send</button>
        </div>

        <div class="pills-container">
            <span class="pill" onclick="quickSend('What time is it?')">⏰ What time is it?</span>
            <span class="pill" onclick="quickSend('Tell me a joke')">😂 Tell me a joke</span>
            <span class="pill" onclick="quickSend('What is today\'s date?')">📅 Today's Date</span>
            <span class="pill" onclick="quickSend('Calculate 45 times 12')">🔢 Calculate 45 * 12</span>
            <span class="pill" onclick="quickSend('Tell me today\'s news headlines')">📰 News Headlines</span>
            <span class="pill" onclick="quickSend('Read my reminders')">📝 Reminders</span>
        </div>

        <div class="tts-toggle">
            <input type="checkbox" id="ttsCheckbox" checked>
            <label for="ttsCheckbox">🔊 Enable Speech Output (Voice Readout)</label>
        </div>
    </div>
</div>

<script>
    const chatLogs = document.getElementById('chatLogs');
    const cmdInput = document.getElementById('cmdInput');
    const micBtn = document.getElementById('micBtn');
    const ttsCheckbox = document.getElementById('ttsCheckbox');

    function appendMessage(sender, text, intent = null) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;
        
        let content = text;
        if (intent && sender === 'assistant') {
            content += `<br><span class="intent-badge">Intent: ${intent}</span>`;
        }
        bubble.innerHTML = content;
        
        chatLogs.appendChild(bubble);
        chatLogs.scrollTop = chatLogs.scrollHeight;
    }

    async function sendCommand(textOverride = null) {
        const text = textOverride || cmdInput.value.trim();
        if (!text) return;

        appendMessage('user', text);
        if (!textOverride) cmdInput.value = '';

        try {
            const res = await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: text, speak: ttsCheckbox.checked })
            });
            const data = await res.json();

            appendMessage('assistant', data.response, data.intent);

            // Optional Web Speech synthesis in browser
            if (ttsCheckbox.checked && 'speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(data.response);
                speechSynthesis.speak(utterance);
            }
        } catch (err) {
            appendMessage('assistant', '⚠️ Unable to connect to Nova backend service.');
        }
    }

    function quickSend(cmd) {
        sendCommand(cmd);
    }

    // Web Speech API Voice Input
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        micBtn.onclick = () => {
            recognition.start();
            micBtn.classList.add('listening');
        };

        recognition.onresult = (event) => {
            micBtn.classList.remove('listening');
            const transcript = event.results[0][0].transcript;
            sendCommand(transcript);
        };

        recognition.onerror = () => {
            micBtn.classList.remove('listening');
        };

        recognition.onend = () => {
            micBtn.classList.remove('listening');
        };
    } else {
        micBtn.title = "Web Speech API not supported in this browser.";
    }
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/command", methods=["POST"])
def process_command():
    data = request.get_json() or {}
    user_command = data.get("command", "").strip()
    should_speak = data.get("speak", False)

    if not user_command:
        return jsonify({"intent": "empty", "response": "Please enter or speak a valid command."})

    intent_name, response_text = intent_matcher.process_command(user_command)

    if should_speak and response_text:
        try:
            speaker.speak(response_text)
        except Exception as e:
            logging.error(f"Speech error: {e}")

    return jsonify({
        "intent": intent_name,
        "response": response_text,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify({
        "assistant_name": config.ASSISTANT_NAME,
        "wake_word": config.WAKE_WORD,
        "tts_engine": config.TTS_ENGINE,
        "stt_engine": config.STT_ENGINE,
        "status": "online"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Nova Voice Virtual Assistant Web Dashboard on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
