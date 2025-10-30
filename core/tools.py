"""
Tool Manager
Implements various tools: Weather, Calculator, Reminder, Search
"""
import os
import json
import logging
import requests
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolManager:
    """Manages and executes various tools"""
    
    def __init__(self):
        self.tools = {
            'weather': self.get_weather,
            'calculator': self.calculate,
            'reminder': self.set_reminder,
            'search': self.search_web
        }
        
        # Initialize reminder storage
        self.reminder_file = os.getenv('REMINDER_FILE', './data/reminders.json')
        os.makedirs(os.path.dirname(self.reminder_file), exist_ok=True)
        
        if not os.path.exists(self.reminder_file):
            with open(self.reminder_file, 'w') as f:
                json.dump({}, f)
        
        logger.info("Tool Manager initialized")
    
    def get_tools_description(self) -> str:
        """Return description of available tools"""
        return """
1. weather: location - Get current weather for a location
   Example: weather: New York
   
2. calculator: expression - Calculate water needs, pH, etc.
   Example: calculator: 5 * 2.5 (liters per plant)
   
3. reminder: schedule - Set watering reminder
   Example: reminder: Water tomatoes every 3 days
   
4. search: query - Search for plant information online
   Example: search: rare orchid care tips
"""
    
    def execute_tool(self, tool_name: str, params: str, user_id: str = None) -> str:
        """Execute a tool and return result"""
        tool_name = tool_name.lower().strip()
        
        if tool_name not in self.tools:
            return f"Unknown tool: {tool_name}"
        
        try:
            logger.info(f"Executing tool: {tool_name} with params: {params}")
            result = self.tools[tool_name](params, user_id)
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {e}", exc_info=True)
            return f"Tool execution failed: {str(e)}"
    
    def get_weather(self, location: str, user_id: str = None) -> str:
        """Get weather information from OpenWeatherMap API"""
        api_key = os.getenv('WEATHER_API_KEY')
        
        if not api_key:
            return "Weather API key not configured"
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location.strip(),
                'appid': api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            
            result = f"Weather in {location}:\n" \
                    f"Temperature: {temp}°C (feels like {feels_like}°C)\n" \
                    f"Conditions: {description}\n" \
                    f"Humidity: {humidity}%\n" \
                    f"Wind: {wind_speed} m/s\n\n"
            
            # Add watering advice based on weather
            if humidity < 40 or temp > 30:
                result += "Plants may need extra watering due to dry/hot conditions."
            elif description in ['rain', 'drizzle', 'thunderstorm']:
                result += "Rain expected - you can skip watering today."
            else:
                result += "Good conditions for regular watering schedule."
            
            logger.info(f"Weather retrieved for {location}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {e}")
            return f"Could not retrieve weather for {location}. Please check the location name."
        except KeyError as e:
            logger.error(f"Weather data parsing error: {e}")
            return "Weather data format error"
    
    def calculate(self, expression: str, user_id: str = None) -> str:
        """Safe calculator for garden-related calculations"""
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Safety: only allow numbers and basic operators
            allowed_chars = set('0123456789+-*/(). ')
            if not all(c in allowed_chars for c in expression):
                return "Invalid calculation expression. Use only numbers and +, -, *, /, (, )"
            
            # Evaluate
            result = eval(expression)
            
            logger.info(f"Calculation: {expression} = {result}")
            return f"Result: {result}"
            
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return f"Calculation error: {str(e)}"
    
    def set_reminder(self, schedule: str, user_id: str = None) -> str:
        """Set a watering reminder for user"""
        if not user_id:
            return "User ID required for reminders"
        
        try:
            # Load existing reminders
            with open(self.reminder_file, 'r') as f:
                reminders = json.load(f)
            
            if user_id not in reminders:
                reminders[user_id] = []
            
            # Create reminder
            reminder = {
                'schedule': schedule.strip(),
                'created_at': datetime.now().isoformat(),
                'active': True
            }
            
            reminders[user_id].append(reminder)
            
            # Save
            with open(self.reminder_file, 'w') as f:
                json.dump(reminders, f, indent=2)
            
            logger.info(f"Reminder set for user {user_id}: {schedule}")
            return f"Reminder set: {schedule}"
            
        except Exception as e:
            logger.error(f"Failed to set reminder: {e}")
            return f"Failed to set reminder: {str(e)}"
    
    def search_web(self, query: str, user_id: str = None) -> str:
        """Search the web using DuckDuckGo (if enabled)"""
        if os.getenv('DUCKDUCKGO_SEARCH_ENABLED', 'false').lower() != 'true':
            return "Web search is not enabled. Enable it in .env to use this feature."
        
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
            
            if not results:
                return "No results found"
            
            output = f"Search results for '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                output += f"{i}. {result['title']}\n"
                output += f"   {result['body'][:150]}...\n"
                output += f"   {result['href']}\n\n"
            
            logger.info(f"Web search completed: {query}")
            return output
            
        except ImportError:
            return "DuckDuckGo search library not installed. Install with: pip install duckduckgo-search"
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Search failed: {str(e)}"
    
    def get_user_reminders(self, user_id: str) -> list:
        """Get all reminders for a user"""
        try:
            with open(self.reminder_file, 'r') as f:
                reminders = json.load(f)
            
            return reminders.get(user_id, [])
        except Exception as e:
            logger.error(f"Failed to get reminders: {e}")
            return []