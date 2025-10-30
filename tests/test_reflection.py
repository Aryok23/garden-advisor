"""
Unit tests for Reflection mechanism
Tests the agent's ability to self-review and improve responses
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent import GardenAdvisorAgent

@pytest.fixture
def agent():
    """Create agent instance"""
    if not os.getenv('GROQ_API_KEY'):
        pytest.skip("GROQ_API_KEY not set")
    
    return GardenAdvisorAgent()

def test_reflection_function_exists(agent):
    """Test that reflection method exists"""
    assert hasattr(agent, '_reflect_on_response')
    assert callable(agent._reflect_on_response)

def test_reflection_returns_string(agent):
    """Test reflection returns a string response"""
    query = "How do I water plants?"
    response = "Water them daily."
    
    reflected = agent._reflect_on_response(query, response)
    
    assert isinstance(reflected, str)
    assert len(reflected) > 0

def test_reflection_preserves_good_response(agent):
    """Test reflection keeps good responses mostly unchanged"""
    query = "What is a tomato?"
    good_response = "A tomato is a fruit that grows on vines, commonly used as a vegetable in cooking."
    
    reflected = agent._reflect_on_response(query, good_response)
    
    # Should contain key information
    assert len(reflected) > 0
    # Good responses should remain similar
    assert any(word in reflected.lower() for word in ['tomato', 'fruit', 'vegetable'])

def test_reflection_handles_errors_gracefully():
    """Test reflection handles errors without crashing"""
    # Create agent without API key to force error
    old_key = os.environ.get('GROQ_API_KEY')
    os.environ['GROQ_API_KEY'] = 'invalid_key'
    
    try:
        agent = GardenAdvisorAgent()
        result = agent._reflect_on_response("test", "test response")
        
        # Should return something even on error (original response)
        assert isinstance(result, str)
    finally:
        if old_key:
            os.environ['GROQ_API_KEY'] = old_key

def test_reflection_improves_incorrect_info():
    """Test reflection on clearly incorrect information"""
    # This requires actual LLM call
    pytest.skip("Requires live API call - integration test")

def test_reflection_adds_missing_info():
    """Test reflection adds missing important information"""
    # This requires actual LLM call
    pytest.skip("Requires live API call - integration test")

def test_reflection_corrects_tone():
    """Test reflection improves response tone"""
    # This requires actual LLM call
    pytest.skip("Requires live API call - integration test")

def test_reflection_in_process_message():
    """Test that reflection is called during message processing"""
    # We can check this by verifying the method exists and is used
    # Full test requires API call
    pytest.skip("Requires live API call - integration test")

def test_multiple_reflections():
    """Test multiple reflection iterations if needed"""
    # Advanced feature - may not be implemented
    pytest.skip("Advanced feature - optional")

def test_reflection_metadata():
    """Test that reflection process is logged"""
    # Check if reflection is logged properly
    pytest.skip("Requires log inspection")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])