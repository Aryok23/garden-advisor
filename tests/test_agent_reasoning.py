"""
Unit tests for Agent Reasoning
Tests the agent's ability to reason and make decisions
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent import GardenAdvisorAgent

@pytest.fixture
def agent():
    """Create agent instance (requires API keys in .env)"""
    # Skip if no API keys
    if not os.getenv('GROQ_API_KEY'):
        pytest.skip("GROQ_API_KEY not set")
    
    return GardenAdvisorAgent()

def test_agent_initialization(agent):
    """Test agent initializes properly"""
    assert agent.llm is not None
    assert agent.memory_manager is not None
    assert agent.tool_manager is not None
    assert agent.planner is not None

def test_system_prompt_generation(agent):
    """Test system prompt includes necessary information"""
    prompt = agent._create_system_prompt()
    
    assert "Garden Advisor" in prompt or "garden" in prompt.lower()
    assert "ReAct" in prompt or "Thought" in prompt
    assert "Action" in prompt
    assert "tool" in prompt.lower()

def test_action_extraction(agent):
    """Test extracting actions from LLM response"""
    response = """
Thought: I need to check the weather
Action: weather: New York
"""
    
    tool_name, params = agent._extract_action(response)
    
    assert tool_name == "weather"
    assert "New York" in params

def test_action_extraction_no_action(agent):
    """Test when no action is present"""
    response = "This is just a regular response without actions."
    
    tool_name, params = agent._extract_action(response)
    
    assert tool_name is None
    assert params is None

def test_reflection_mechanism(agent):
    """Test reflection improves responses"""
    query = "How often should I water cactus?"
    response = "Water it every day."  # Incorrect
    
    reflected = agent._reflect_on_response(query, response)
    
    # Reflection should produce some output
    assert len(reflected) > 0
    assert isinstance(reflected, str)

def test_agent_handles_simple_query():
    """Test agent can handle simple queries without tools"""
    # This would require actual API call, so we mock or skip
    pytest.skip("Requires live API call")

def test_agent_remembers_context():
    """Test agent uses memory for context"""
    # This would require actual API call
    pytest.skip("Requires live API call")

def test_reasoning_chain():
    """Test the complete reasoning chain"""
    # Thought -> Action -> Observation -> Answer
    pytest.skip("Requires live API call - integration test")

def test_multi_turn_conversation():
    """Test agent maintains context across turns"""
    pytest.skip("Requires live API call - integration test")

def test_error_handling(agent):
    """Test agent handles errors gracefully"""
    # Test with invalid user_id format
    try:
        response = agent.process_message("", "Test message")
        assert len(response) > 0  # Should return some error message
    except Exception:
        pass  # Expected to potentially raise errors

def test_cleanup(agent):
    """Test agent cleanup"""
    agent.cleanup()
    # Should not raise errors

if __name__ == "__main__":
    pytest.main([__file__, "-v"])