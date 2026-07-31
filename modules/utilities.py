import os
import json
import time
import subprocess
import datetime
import logging
import pyjokes
import config

logger = logging.getLogger(__name__)

class UtilitiesHandler:
    """
    Handles date/time, local app opening, reminder management, jokes, and casual responses.
    """

    def __init__(self):
        self.reminders_path = config.REMINDERS_FILE

    def get_current_time(self) -> str:
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"The current time is {time_str}."

    def get_current_date(self) -> str:
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today is {date_str}."

    def tell_joke(self) -> str:
        try:
            joke = pyjokes.get_joke()
            return f"Here is a joke for you: {joke}"
        except Exception as e:
            logger.error(f"pyjokes error: {e}")
            return "Why don't scientists trust atoms? Because they make up everything!"

    def open_local_app(self, app_name: str) -> str:
        """
        Open common system applications (Notepad, Calculator, Command Prompt, etc.).
        """
        clean_app = app_name.lower().strip()

        # Windows app mapping
        app_commands = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "command prompt": "cmd.exe",
            "cmd": "cmd.exe",
            "paint": "mspaint.exe",
            "explorer": "explorer.exe",
        }

        cmd = app_commands.get(clean_app)
        if cmd:
            try:
                subprocess.Popen(cmd, shell=True)
                logger.info(f"Launched local app: {cmd}")
                return f"Opening {clean_app}."
            except Exception as e:
                logger.error(f"Failed to launch application {cmd}: {e}")
                return f"Sorry, I couldn't open {clean_app}."
        else:
            return f"I don't know how to open {app_name}. You can configure it in application mappings."

    def add_reminder(self, reminder_text: str) -> str:
        """
        Save a new reminder to data/reminders.json.
        """
        if not reminder_text:
            return "What would you like me to remind you about?"

        reminders = self._load_reminders()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"timestamp": timestamp, "text": reminder_text.strip()}
        reminders.append(entry)

        try:
            with open(self.reminders_path, "w", encoding="utf-8") as f:
                json.dump(reminders, f, indent=2)
            logger.info(f"Added reminder: {reminder_text}")
            return f"I have set a reminder: '{reminder_text}'."
        except Exception as e:
            logger.error(f"Failed to save reminder: {e}")
            return "Failed to save the reminder."

    def list_reminders(self) -> str:
        """
        Read out saved reminders.
        """
        reminders = self._load_reminders()
        if not reminders:
            return "You have no saved reminders."

        items = [f"{i+1}. {r['text']} (added {r['timestamp']})" for i, r in enumerate(reminders)]
        return f"You have {len(reminders)} reminders: " + "; ".join(items)

    def clear_reminders(self) -> str:
        try:
            with open(self.reminders_path, "w", encoding="utf-8") as f:
                json.dump([], f)
            return "All reminders have been cleared."
        except Exception as e:
            logger.error(f"Error clearing reminders: {e}")
            return "Failed to clear reminders."

    def _load_reminders(self) -> list:
        if not self.reminders_path.exists():
            return []
        try:
            with open(self.reminders_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading reminders.json: {e}")
            return []

    def get_greeting(self) -> str:
        hour = datetime.datetime.now().hour
        if hour < 12:
            time_of_day = "Good morning"
        elif hour < 18:
            time_of_day = "Good afternoon"
        else:
            time_of_day = "Good evening"
        return f"{time_of_day}! How can I help you today?"
