import ast
import operator
import logging
import requests
from bs4 import BeautifulSoup
import config

logger = logging.getLogger(__name__)

class SafeCalculator(ast.NodeVisitor):
    """
    Safely evaluate math expressions using AST parsing without raw eval().
    """

    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(self, expression: str):
        # Replace spoken math words with operators
        expr_clean = (
            expression.lower()
            .replace("plus", "+")
            .replace("minus", "-")
            .replace("times", "*")
            .replace("multiplied by", "*")
            .replace("divided by", "/")
            .replace("x", "*")
            .replace("into", "*")
            .strip()
        )
        try:
            node = ast.parse(expr_clean, mode="eval")
            return self.visit(node.body)
        except Exception as e:
            logger.error(f"Safe calculator evaluation error for '{expression}': {e}")
            return None

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type in self.ALLOWED_OPERATORS:
            return self.ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type}")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type in self.ALLOWED_OPERATORS:
            return self.ALLOWED_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Invalid constant: {node.value}")

    def visit_Num(self, node):  # Python < 3.8 fallback
        return node.n


class WebSearchHandler:
    """
    Handles Wikipedia queries, Weather API, News API, and safe math evaluations.
    """

    def __init__(self):
        self.calculator = SafeCalculator()

    def search_wikipedia(self, query: str, sentences: int = 2) -> str:
        """
        Search Wikipedia for a query and return a concise summary.
        """
        if not query:
            return "What would you like me to look up on Wikipedia?"

        try:
            import wikipedia
            wikipedia.set_lang("en")
            summary = wikipedia.summary(query, sentences=sentences)
            return f"According to Wikipedia: {summary}"
        except Exception as e:
            logger.info(f"wikipedia-python package failed or not available: {e}. Falling back to REST API.")
            return self._wikipedia_rest_fallback(query)

    def _wikipedia_rest_fallback(self, query: str) -> str:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            headers = {"User-Agent": "VoiceAssistantBot/1.0"}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                extract = data.get("extract", "")
                if extract:
                    return f"According to Wikipedia: {extract[:300]}..."
            return f"I couldn't find a detailed Wikipedia summary for '{query}'."
        except Exception as err:
            logger.error(f"Wikipedia REST API error: {err}")
            return "I couldn't connect to Wikipedia right now."

    def get_weather(self, city: str = "") -> str:
        """
        Get weather info for specified city using OpenWeatherMap API or fallback search.
        """
        target_city = city.strip() if city else config.DEFAULT_CITY

        if config.OPENWEATHER_API_KEY:
            try:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={target_city}&appid={config.OPENWEATHER_API_KEY}&units=metric"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"]
                    humidity = data["main"]["humidity"]
                    return f"The weather in {target_city} is currently {desc} with a temperature of {temp} degrees Celsius and {humidity}% humidity."
                elif response.status_code == 404:
                    return f"I couldn't find weather details for city '{target_city}'."
            except Exception as e:
                logger.error(f"OpenWeather API error: {e}")

        # Fallback to web scraping weather summary if API key is not set or failed
        return self._scrape_weather_fallback(target_city)

    def _scrape_weather_fallback(self, city: str) -> str:
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geo_res = requests.get(geo_url, timeout=5)
            if geo_res.status_code == 200:
                geo_data = geo_res.json()
                results = geo_data.get("results", [])
                if results:
                    loc = results[0]
                    lat = loc.get("latitude")
                    lon = loc.get("longitude")
                    city_name = loc.get("name", city)
                    country = loc.get("country", "")
                    
                    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                    w_res = requests.get(weather_url, timeout=5)
                    if w_res.status_code == 200:
                        w_data = w_res.json().get("current_weather", {})
                        temp = w_data.get("temperature")
                        wind = w_data.get("windspeed")
                        c_info = f", {country}" if country else ""
                        return f"The current weather in {city_name}{c_info} is {temp}°C with wind speed of {wind} km/h."
            return f"I couldn't find weather details for city '{city}'."
        except Exception as e:
            logger.error(f"Weather fallback API error: {e}")
            return "I couldn't reach the weather service right now."


    def get_news_headlines(self, category: str = "general", max_articles: int = 3) -> str:
        """
        Fetch top news headlines using NewsAPI or Google News RSS fallback.
        """
        if config.NEWS_API_KEY:
            try:
                url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={config.NEWS_API_KEY}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])[:max_articles]
                    if articles:
                        headlines = [f"Headline {i+1}: {art['title']}" for i, art in enumerate(articles)]
                        return "Here are today's top news headlines: " + ". ".join(headlines)
            except Exception as e:
                logger.error(f"NewsAPI error: {e}")

        # Fallback news fetcher
        return self._fetch_news_rss_fallback(max_articles)

    def _fetch_news_rss_fallback(self, max_articles: int = 3) -> str:
        try:
            rss_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(rss_url, headers=headers, timeout=5)
            if res.status_code == 200:
                try:
                    soup = BeautifulSoup(res.content, "xml")
                except Exception:
                    import warnings
                    from bs4 import XMLParsedAsHTMLWarning
                    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
                    soup = BeautifulSoup(res.content, "html.parser")

                items = soup.find_all("item")[:max_articles]
                if items:
                    headlines = [f"Headline {i+1}: {item.title.text.strip()}" for i, item in enumerate(items) if item.title]
                    return "Here are top news headlines: " + ". ".join(headlines)
            return "I couldn't retrieve the news at this moment."
        except Exception as e:
            logger.error(f"News RSS fallback error: {e}")
            return "I couldn't reach the news service right now."


    def calculate_math(self, math_expression: str) -> str:
        """
        Evaluate mathematical expressions safely without raw eval().
        """
        result = self.calculator.evaluate(math_expression)
        if result is not None:
            return f"The result of {math_expression} is {result}."
        return f"Sorry, I couldn't evaluate the mathematical expression '{math_expression}'."
