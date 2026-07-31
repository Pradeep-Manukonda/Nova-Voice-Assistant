import logging
import urllib.parse
import webbrowser
import config

logger = logging.getLogger(__name__)

class BrowserController:
    """
    Handles website launching, web searches, and YouTube play commands.
    """

    KNOWN_SITES = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://www.github.com",
        "stack overflow": "https://stackoverflow.com",
        "wikipedia": "https://www.wikipedia.org",
        "reddit": "https://www.reddit.com",
        "gmail": "https://mail.google.com",
    }

    def open_website(self, site_name_or_url: str) -> str:
        """
        Open a requested website in default web browser.
        """
        clean = site_name_or_url.strip().lower()

        # Check known site mapping
        if clean in self.KNOWN_SITES:
            url = self.KNOWN_SITES[clean]
            webbrowser.open(url)
            logger.info(f"Opened site mapping: {clean} -> {url}")
            return f"Opening {clean} in your web browser."

        # Handle full URL or domain
        if clean.startswith("http://") or clean.startswith("https://"):
            url = clean
        elif "." in clean and not " " in clean:
            url = f"https://{clean}"
        else:
            # Fallback to Google search
            return self.search_google(site_name_or_url)

        try:
            webbrowser.open(url)
            logger.info(f"Opened URL: {url}")
            return f"Opening {site_name_or_url}."
        except Exception as e:
            logger.error(f"Error opening URL {url}: {e}")
            return f"Failed to open website {site_name_or_url}."

    def search_google(self, query: str) -> str:
        """
        Construct a Google search URL and open in browser.
        """
        if not query:
            return "What would you like to search Google for?"

        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        try:
            webbrowser.open(search_url)
            logger.info(f"Opened Google search: {query}")
            return f"Searching Google for {query}."
        except Exception as e:
            logger.error(f"Google search launch error: {e}")
            return "Failed to perform Google search."

    def play_youtube(self, topic_or_song: str) -> str:
        """
        Search and play video/song on YouTube using pywhatkit or fallback search URL.
        """
        if not topic_or_song:
            return "What video or song would you like me to play on YouTube?"

        try:
            import pywhatkit
            pywhatkit.playonyt(topic_or_song)
            logger.info(f"Playing YouTube query via pywhatkit: {topic_or_song}")
            return f"Playing {topic_or_song} on YouTube."
        except Exception as e:
            logger.info(f"pywhatkit playonyt failed: {e}. Opening search URL fallback.")
            encoded = urllib.parse.quote_plus(topic_or_song)
            yt_url = f"https://www.youtube.com/results?search_query={encoded}"
            webbrowser.open(yt_url)
            return f"Searching YouTube for {topic_or_song}."
