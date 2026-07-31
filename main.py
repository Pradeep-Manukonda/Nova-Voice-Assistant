import sys
import argparse
import logging
import signal
import config

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')


from speech import Speaker, Listener
from modules import EmailHandler, WebSearchHandler, BrowserController, UtilitiesHandler
from intents import IntentMatcher

# Setup Logging
logging.basicConfig(
    filename=config.LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("MainAssistant")

def print_banner():
    banner = f"""
    ========================================================
             🤖 {config.ASSISTANT_NAME} - VOICE VIRTUAL ASSISTANT 🤖
    ========================================================
     Wake Word: "{config.WAKE_WORD}"
     TTS Engine: {config.TTS_ENGINE}
     STT Engine: {config.STT_ENGINE}
    ========================================================
    """
    print(banner)

def main():
    parser = argparse.ArgumentParser(description=f"{config.ASSISTANT_NAME} Voice Virtual Assistant")
    parser.add_argument("--text", action="store_true", help="Run in terminal text-input mode (no microphone required)")
    args = parser.parse_args()

    print_banner()
    logger.info("Initializing Assistant components...")

    # Initialize Modules
    speaker = Speaker()
    listener = Listener(text_mode=args.text)

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

    # Initial Ambient Noise Calibration
    if not listener.text_mode:
        listener.calibrate_ambient_noise(duration=1)

    initial_greeting = utilities.get_greeting()
    speaker.speak(f"{initial_greeting} Say '{config.WAKE_WORD}' or speak your command.")

    # Graceful Signal Handling
    def signal_handler(sig, frame):
        print("\nShutting down assistant...")
        speaker.speak("Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Main Listen-Process-Respond Loop
    running = True
    while running:
        try:
            # Check if user typed a command in text mode during wake word prompt
            typed_cmd = listener.get_last_typed_command()
            if typed_cmd:
                command_text = typed_cmd
            else:
                if not listener.text_mode:
                    print(f"\n💤 Waiting for wake word ('{config.WAKE_WORD}')...")
                    if not listener.listen_for_wakeword():
                        continue

                    speaker.speak("Yes? I am listening.")

                command_text = listener.listen_command()

            if not command_text:
                continue

            if command_text == "__unrecognized__":
                speaker.speak("I didn't quite catch that. Could you please repeat?")
                continue

            if command_text == "__network_error__":
                speaker.speak("Speech recognition service seems to be offline.")
                continue

            # Process intent and route to handler
            intent_name, response_text = intent_matcher.process_command(command_text)

            if response_text:
                speaker.speak(response_text)

            if intent_name == "exit":
                logger.info("Exit command received. Shutting down loop.")
                running = False

        except (KeyboardInterrupt, SystemExit):
            print("\nShutting down assistant...")
            speaker.speak("Goodbye!")
            break
        except Exception as e:
            logger.critical(f"Unhandled error in main loop: {e}", exc_info=True)
            speaker.speak("An unexpected error occurred. Restarting command listener.")

if __name__ == "__main__":
    main()
