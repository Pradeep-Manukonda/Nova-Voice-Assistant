import re
import logging
from typing import Callable, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class IntentMatcher:
    """
    Lightweight NLU intent classification system based on regex & keyword rules.
    Designed with a registry pattern so new intent rules and handlers can easily be added.
    Supports optional upgrade path to spaCy or ML intent classification models.
    """

    def __init__(self, email_handler, web_search, browser_control, utilities):
        self.email_handler = email_handler
        self.web_search = web_search
        self.browser_control = browser_control
        self.utilities = utilities

        # Command Registry: list of (intent_name, regex_pattern, handler_func)
        self.rules = []
        self._register_default_rules()

    def register_intent(self, intent_name: str, pattern: str, handler: Callable):
        """
        Register a new intent pattern and its target handler function.
        """
        compiled_regex = re.compile(pattern, re.IGNORECASE)
        self.rules.append((intent_name, compiled_regex, handler))
        logger.debug(f"Registered intent '{intent_name}' with pattern '{pattern}'")

    def _register_default_rules(self):
        # Exit / Termination Intents
        self.register_intent("exit", r"\b(exit|quit|stop|goodbye|bye|shut down|terminate)\b", self._handle_exit)

        # Email Intents
        self.register_intent("send_email", r"(send (an )?email|email to|mail to)", self._handle_send_email)
        self.register_intent("read_email", r"(read|check|get) (my |unread )?emails?", self._handle_read_email)

        # YouTube & Browsing Intents
        self.register_intent("play_youtube", r"(play|search) (.+) on youtube|play (.+)", self._handle_play_youtube)
        self.register_intent("google_search", r"(search google for|google search|search for) (.+)", self._handle_google_search)
        self.register_intent("open_website", r"open (https?://\S+|\S+\.\S+|youtube|google|github|reddit|gmail|wikipedia)", self._handle_open_website)

        # Information Retrieval Intents
        self.register_intent("weather", r"(weather|temperature|forecast)( in| for)? ?([a-zA-Z\s]*)", self._handle_weather)
        self.register_intent("news", r"(news|headlines|latest news)", self._handle_news)
        self.register_intent("wikipedia", r"(who is|what is|tell me about|wikipedia|search wikipedia for) (.+)", self._handle_wikipedia)
        self.register_intent("math", r"(calculate|eval|what is|solve) ([\d\s\+\-\*\/\(\)x\.]+|.+plus.+|.+minus.+|.+times.+|.+divided by.+)", self._handle_math)

        # System & Utility Intents
        self.register_intent("time", r"(current time|what time|time is it|tell me the time)", self._handle_time)
        self.register_intent("date", r"(what is today's date|today's date|what date|what day is it)", self._handle_date)
        self.register_intent("open_app", r"(?:open|launch|run|start)?\s*\b(notepad|calculator|calc|cmd|command prompt|paint|explorer)\b", self._handle_open_app)
        self.register_intent("joke", r"(tell me a joke|tell a joke|say something funny|joke)", self._handle_joke)
        self.register_intent("reminder_add", r"(remind me to|set (a )?reminder (to|for)) (.+)", self._handle_add_reminder)
        self.register_intent("reminder_list", r"(read|list|show|get) (my )?reminders", self._handle_list_reminders)
        self.register_intent("reminder_clear", r"(clear|delete|remove) (all )?reminders", self._handle_clear_reminders)
        self.register_intent("greeting", r"\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b", self._handle_greeting)

    def process_command(self, text: str) -> Tuple[str, str]:
        """
        Parse recognised command text, match intent, and execute corresponding handler.
        Returns a tuple of (intent_name, spoken_response_string).
        """
        clean_text = text.strip().rstrip(".!?,")

        if not clean_text:
            return ("empty", "")

        # Test registered intent patterns
        for intent_name, regex, handler in self.rules:
            match = regex.search(clean_text)
            if match:
                logger.info(f"Matched intent '{intent_name}' for input: '{text}'")
                try:
                    response = handler(clean_text, match)
                    return (intent_name, response)
                except Exception as e:
                    logger.error(f"Error handling intent '{intent_name}': {e}")
                    return (intent_name, "I encountered an issue processing that command.")

        # Fallback to general search or Wikipedia if no explicit intent matched
        logger.info(f"No specific intent matched for '{text}'. Falling back to search.")
        return ("fallback", self.web_search.search_wikipedia(text))

    # --- INTENT HANDLERS ---

    def _handle_exit(self, text: str, match: re.Match) -> str:
        return "Goodbye! Have a great day."

    def _handle_send_email(self, text: str, match: re.Match) -> str:
        # Simple extraction: "send email to [contact] saying [message]"
        to_part = ""
        msg_part = ""

        # Regex parsing for "to <name> saying/body <msg>"
        pattern = r"email to ([a-zA-Z0-9\._@]+)(?: saying | body | with message )?(.*)"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            to_part = m.group(1).strip()
            msg_part = m.group(2).strip()

        if not to_part:
            return "Who would you like to send an email to?"
        if not msg_part:
            msg_part = "Hello, this is an automated message sent by your Voice Assistant."

        return self.email_handler.send_email(to_part, "Voice Assistant Message", msg_part)

    def _handle_read_email(self, text: str, match: re.Match) -> str:
        return self.email_handler.read_unread_emails()

    def _handle_play_youtube(self, text: str, match: re.Match) -> str:
        groups = [g for g in match.groups() if g]
        query = groups[-1] if groups else ""
        return self.browser_control.play_youtube(query)

    def _handle_google_search(self, text: str, match: re.Match) -> str:
        groups = [g for g in match.groups() if g]
        query = groups[-1] if groups else ""
        return self.browser_control.search_google(query)

    def _handle_open_website(self, text: str, match: re.Match) -> str:
        groups = [g for g in match.groups() if g]
        site = groups[0] if groups else text
        return self.browser_control.open_website(site)

    def _handle_weather(self, text: str, match: re.Match) -> str:
        city = match.group(3).strip() if match.lastindex >= 3 else ""
        return self.web_search.get_weather(city)

    def _handle_news(self, text: str, match: re.Match) -> str:
        return self.web_search.get_news_headlines()

    def _handle_wikipedia(self, text: str, match: re.Match) -> str:
        query = match.group(2).strip() if match.lastindex >= 2 else text
        return self.web_search.search_wikipedia(query)

    def _handle_math(self, text: str, match: re.Match) -> str:
        expr = match.group(2).strip() if match.lastindex >= 2 else text
        return self.web_search.calculate_math(expr)

    def _handle_time(self, text: str, match: re.Match) -> str:
        return self.utilities.get_current_time()

    def _handle_date(self, text: str, match: re.Match) -> str:
        return self.utilities.get_current_date()

    def _handle_open_app(self, text: str, match: re.Match) -> str:
        app = match.group(1).strip() if match.lastindex >= 1 else text
        return self.utilities.open_local_app(app)


    def _handle_joke(self, text: str, match: re.Match) -> str:
        return self.utilities.tell_joke()

    def _handle_add_reminder(self, text: str, match: re.Match) -> str:
        reminder_text = match.group(4).strip() if match.lastindex >= 4 else text
        return self.utilities.add_reminder(reminder_text)

    def _handle_list_reminders(self, text: str, match: re.Match) -> str:
        return self.utilities.list_reminders()

    def _handle_clear_reminders(self, text: str, match: re.Match) -> str:
        return self.utilities.clear_reminders()

    def _handle_greeting(self, text: str, match: re.Match) -> str:
        return self.utilities.get_greeting()
