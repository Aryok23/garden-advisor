"""
Unit tests for Tool Manager
"""
import pytest
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.tools import ToolManager

@pytest.fixture
def temp_reminder_file():
    """Create temporary reminder file"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_file.write('{}')
    temp_file.close()
    os.environ['REMINDER_FILE'] = temp_file.name
    yield temp_file.name
    os.unlink(temp_file.name)

@pytest.fixture
def tool_manager(temp_reminder_file):
    """Create ToolManager instance"""
    return ToolManager()

def test_calculator_tool(tool_manager):
    """Test calculator tool"""
    result = tool_manager.calculate("5 * 2.5")
    
    assert "12.5" in result or "Result: 12.5" in result

def test_calculator_safety(tool_manager):
    """Test calculator rejects unsafe expressions"""
    result = tool_manager.calculate("import os")
    
    assert "Invalid" in result or "error" in result.lower()

def test_calculator_complex_expression(tool_manager):
    """Test calculator with complex expressions"""
    result = tool_manager.calculate("(10 + 5) * 2 / 3")
    
    assert "10" in result  # Should equal 10.0

def test_reminder_tool(tool_manager):
    """Test setting reminders"""
    user_id = "test_user_reminder"
    result = tool_manager.set_reminder("Water tomatoes every 3 days", user_id)
    
    assert "✅" in result or "set" in result.lower()
    
    # Verify reminder was saved
    reminders = tool_manager.get_user_reminders(user_id)
    assert len(reminders) > 0
    assert "tomatoes" in reminders[0]['schedule'].lower()

def test_multiple_reminders_per_user(tool_manager):
    """Test multiple reminders for one user"""
    user_id = "test_multi_reminder"
    
    tool_manager.set_reminder("Water roses daily", user_id)
    tool_manager.set_reminder("Fertilize monthly", user_id)
    
    reminders = tool_manager.get_user_reminders(user_id)
    assert len(reminders) >= 2

def test_weather_tool_without_api_key(tool_manager):
    """Test weather tool without API key"""
    # Clear API key temporarily
    old_key = os.environ.get('WEATHER_API_KEY')
    os.environ['WEATHER_API_KEY'] = ''
    
    result = tool_manager.get_weather("New York")
    
    assert "not configured" in result.lower() or "error" in result.lower()
    
    # Restore
    if old_key:
        os.environ['WEATHER_API_KEY'] = old_key

def test_tool_execution(tool_manager):
    """Test execute_tool dispatcher"""
    result = tool_manager.execute_tool("calculator", "10 + 5", "test_user")
    
    assert "15" in result

def test_invalid_tool(tool_manager):
    """Test executing non-existent tool"""
    result = tool_manager.execute_tool("invalid_tool", "params", "test_user")
    
    assert "Unknown tool" in result

def test_tools_description(tool_manager):
    """Test tools description format"""
    description = tool_manager.get_tools_description()
    
    assert "weather" in description.lower()
    assert "calculator" in description.lower()
    assert "reminder" in description.lower()

def test_search_tool_disabled(tool_manager):
    """Test search tool when disabled"""
    os.environ['DUCKDUCKGO_SEARCH_ENABLED'] = 'false'
    
    result = tool_manager.search_web("test query")
    
    assert "not enabled" in result.lower() or "disabled" in result.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])