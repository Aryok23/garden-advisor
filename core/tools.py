"""
Tool Manager
Implements various tools: Weather, Calculator, Reminder, Search, and Reminder Clearing
"""
import os
import json
import logging
import requests
from typing import Any, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolManager:
    """Manages and executes various tools for Garden Advisor"""

    def __init__(self):
        self.tools = {
            'weather': self.get_weather,
            'calculator': self.calculate,
            'reminder': self.set_reminder,
            'search': self.search_web
        }

        # === Reminder setup ===
        self.reminder_file = os.getenv('REMINDER_FILE', './data/reminders.json')
        os.makedirs(os.path.dirname(self.reminder_file), exist_ok=True)

        if not os.path.exists(self.reminder_file):
            with open(self.reminder_file, 'w') as f:
                json.dump({}, f)

        # Optional in-memory cache for performance
        self._reminder_cache = self._load_reminders()

        logger.info("Tool Manager initialized successfully")

    # ======================================================
    # === Helper functions for reminders file handling ===
    # ======================================================
    def _load_reminders(self) -> Dict[str, List[Dict]]:
        """Load reminders from JSON file safely"""
        try:
            with open(self.reminder_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Reminder file empty or corrupted — resetting.")
            return {}
        except Exception as e:
            logger.error(f"Error loading reminders: {e}")
            return {}

    def _save_reminders(self, reminders: Dict[str, List[Dict]]):
        """Save reminders to JSON file safely"""
        try:
            with open(self.reminder_file, 'w') as f:
                json.dump(reminders, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save reminders: {e}")

    # ======================================================
    # === Public Tool Descriptions ===
    # ======================================================
    def get_tools_description(self) -> str:
        """Return description of available tools"""
        return """
1️. **weather** — Get current weather for a location  
   _Example:_ `weather: New York`

2️. **calculator** — Perform simple arithmetic (e.g., water volume)  
   _Example:_ `calculator: 5 * 2.5`

3️. **reminder** — Set a watering reminder  
   _Example:_ `reminder: Water tomatoes every 3 days`

4️. **search** — Find information about plants online  
   _Example:_ `search: rare orchid care tips`
"""

    # ======================================================
    # === Tool Dispatcher ===
    # ======================================================
    def execute_tool(self, tool_name: str, params: str, user_id: str = None) -> str:
        """Execute a tool dynamically"""
        tool_name = tool_name.lower().strip()

        if tool_name not in self.tools:
            return f"Unknown tool: {tool_name}"

        try:
            logger.info(f"Executing tool: {tool_name} with params: {params}")
            return self.tools[tool_name](params, user_id)
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {e}", exc_info=True)
            return f"Tool execution failed: {str(e)}"

    # ======================================================
    # === Tool Implementations ===
    # ======================================================
    def get_weather(self, location: str, user_id: str = None) -> str:
        """Fetch weather data from OpenWeatherMap"""
        api_key = os.getenv('WEATHER_API_KEY')
        if not api_key:
            return "Weather API key not configured. Please set WEATHER_API_KEY in .env."

        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {'q': location.strip(), 'appid': api_key, 'units': 'metric'}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']

            result = (
                f"**Weather in {location.title()}**\n"
                f"• Temperature: {temp}°C (feels like {feels_like}°C)\n"
                f"• Conditions: {description}\n"
                f"• Humidity: {humidity}%\n"
                f"• Wind Speed: {wind_speed} m/s\n\n"
            )

            # Add contextual watering suggestion
            if humidity < 40 or temp > 30:
                result += "It's quite dry/hot — consider extra watering."
            elif any(x in description.lower() for x in ['rain', 'drizzle', 'thunderstorm']):
                result += "Rain expected — you can skip watering today."
            else:
                result += "Conditions are fine for regular watering."

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {e}")
            return f"Unable to retrieve weather for '{location}'."
        except KeyError:
            return "Unexpected weather data format."

    def calculate(self, expression: str, user_id: str = None) -> str:
        """Perform a safe arithmetic calculation"""
        try:
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                return "Invalid expression. Use only numbers and +, -, *, /, (, )."

            result = eval(expression)
            logger.info(f"Calculation performed: {expression} = {result}")
            return f"Result: `{result}`"
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return f"Calculation error: {str(e)}"

    def set_reminder(self, schedule: str, user_id: str = None) -> str:
        """Set a watering reminder for the user"""
        if not user_id:
            return "User ID required to set reminders."

        try:
            reminders = self._load_reminders()

            reminder = {
                'schedule': schedule.strip(),
                'created_at': datetime.now().isoformat(),
                'active': True
            }

            reminders.setdefault(user_id, []).append(reminder)
            self._save_reminders(reminders)
            self._reminder_cache = reminders  # update in-memory cache

            logger.info(f"Reminder set for user {user_id}: {schedule}")
            return f"Reminder set: **{schedule}**"
        except Exception as e:
            logger.error(f"Failed to set reminder: {e}")
            return f"Failed to set reminder: {str(e)}"

    def search_web(self, query: str, user_id: str = None) -> str:
        """Search the web for plant info using DuckDuckGo"""
        if os.getenv('DUCKDUCKGO_SEARCH_ENABLED', 'false').lower() != 'true':
            return "Web search is disabled. Enable `DUCKDUCKGO_SEARCH_ENABLED=true` in .env."

        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))

            if not results:
                return f"No results found for '{query}'."

            output = f"**Search results for:** `{query}`\n\n"
            for i, result in enumerate(results, 1):
                output += f"**{i}. {result['title']}**\n"
                output += f"{result['body'][:150]}...\n"
                output += f"<{result['href']}>\n\n"

            return output

        except ImportError:
            return "Please install DuckDuckGo Search: `pip install duckduckgo-search`"
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Web search failed: {str(e)}"

    # ======================================================
    # === Reminder Management ===
    # ======================================================
    def get_user_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Return all reminders for a user"""
        try:
            reminders = self._load_reminders()
            return reminders.get(user_id, [])
        except Exception as e:
            logger.error(f"Failed to get reminders: {e}")
            return []

    def get_all_users(self) -> List[str]:
        """Return list of all users who have reminders"""
        try:
            reminders = self._load_reminders()
            return list(reminders.keys())
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    def clear_user_reminders(self, user_id: str):
        """Delete all reminders for a given user"""
        try:
            reminders = self._load_reminders()
            if user_id in reminders:
                del reminders[user_id]
                self._save_reminders(reminders)
                self._reminder_cache = reminders
                logger.info(f"Cleared all reminders for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to clear reminders for user {user_id}: {e}")
