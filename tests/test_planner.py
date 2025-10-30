"""
Unit tests for Planner
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.planner import Planner

@pytest.fixture
def planner():
    """Create Planner instance"""
    return Planner()

def test_weather_query_planning(planner):
    """Test planning for weather-related queries"""
    plan = planner.create_plan("Should I water my plants today in New York?")
    
    assert plan['type'] == 'weather_check'
    assert plan['requires_tools'] == True
    assert len(plan['steps']) > 0

def test_plant_care_query_planning(planner):
    """Test planning for plant care queries"""
    plan = planner.create_plan("How do I care for tomatoes?")
    
    assert plan['type'] == 'plant_care'
    assert any('plant' in step.lower() or 'knowledge' in step.lower() for step in plan['steps'])

def test_reminder_query_planning(planner):
    """Test planning for reminder queries"""
    plan = planner.create_plan("Remind me to water roses every 3 days")
    
    assert plan['type'] == 'reminder'
    assert plan['requires_tools'] == True

def test_calculation_query_planning(planner):
    """Test planning for calculation queries"""
    plan = planner.create_plan("Calculate how much water for 5 plants")
    
    assert plan['type'] == 'calculation'
    assert plan['requires_tools'] == True

def test_search_query_planning(planner):
    """Test planning for search queries"""
    plan = planner.create_plan("Search for rare orchid care tips")
    
    assert plan['type'] == 'search'
    assert plan['requires_tools'] == True

def test_general_query_planning(planner):
    """Test planning for general queries"""
    plan = planner.create_plan("Hello, how are you?")
    
    assert plan['type'] == 'general'
    assert plan['requires_tools'] == False

def test_plan_structure(planner):
    """Test that plans have correct structure"""
    plan = planner.create_plan("Test query")
    
    assert 'query' in plan
    assert 'type' in plan
    assert 'steps' in plan
    assert 'requires_tools' in plan
    assert 'estimated_complexity' in plan
    assert isinstance(plan['steps'], list)

def test_plan_complexity_estimation(planner):
    """Test complexity estimation"""
    simple_plan = planner.create_plan("Hello")
    complex_plan = planner.create_plan("Check weather and calculate water needs")
    
    assert simple_plan['estimated_complexity'] in ['low', 'medium', 'high']
    assert complex_plan['estimated_complexity'] in ['low', 'medium', 'high']

def test_plan_adjustment(planner):
    """Test plan adjustment based on feedback"""
    plan = planner.create_plan("Test query")
    adjusted = planner.adjust_plan(plan, "error occurred")
    
    assert 'Retry' in str(adjusted['steps']) or adjusted['estimated_complexity'] == 'high'

def test_multiple_keywords_query(planner):
    """Test query with multiple keywords"""
    plan = planner.create_plan("Should I water my tomatoes? Check the weather first.")
    
    # Should prioritize weather check
    assert plan['type'] in ['weather_check', 'plant_care']

if __name__ == "__main__":
    pytest.main([__file__, "-v"])