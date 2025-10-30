"""
Unit tests for Memory Management
"""
import pytest
import os
import sys
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.memory import MemoryManager

@pytest.fixture
def temp_chroma_path():
    """Create temporary ChromaDB path"""
    temp_dir = tempfile.mkdtemp()
    os.environ['CHROMA_DB_PATH'] = temp_dir
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def memory_manager(temp_chroma_path):
    """Create MemoryManager instance for testing"""
    return MemoryManager()

def test_short_term_memory_storage(memory_manager):
    """Test short-term memory storage and retrieval"""
    user_id = "test_user_123"
    
    # Add conversation
    memory_manager.add_to_short_term_memory(
        user_id, 
        "How do I care for tomatoes?",
        "Water tomatoes every 2-3 days..."
    )
    
    # Retrieve
    history = memory_manager.get_short_term_memory(user_id)
    
    assert len(history) == 2  # Human + AI message
    assert "tomatoes" in history[0].content.lower()
    assert "water" in history[1].content.lower()

def test_short_term_memory_limit(memory_manager):
    """Test that short-term memory respects max limit"""
    user_id = "test_user_456"
    
    # Add many messages
    for i in range(15):
        memory_manager.add_to_short_term_memory(
            user_id,
            f"Question {i}",
            f"Answer {i}"
        )
    
    history = memory_manager.get_short_term_memory(user_id)
    
    # Should only keep last 20 messages (10 pairs)
    assert len(history) <= 20

def test_long_term_memory_storage(memory_manager):
    """Test long-term memory storage in ChromaDB"""
    user_id = "test_user_789"
    
    memory_manager.add_to_long_term_memory(
        user_id,
        "What about roses?",
        "Roses need full sunlight..."
    )
    
    # Query relevant memory
    relevant = memory_manager.get_relevant_long_term_memory(user_id, "roses")
    
    assert "roses" in relevant.lower() or "Roses" in relevant

def test_per_user_memory_isolation(memory_manager):
    """Test that memory is isolated per user"""
    user1 = "user_001"
    user2 = "user_002"
    
    # Add different data for each user
    memory_manager.add_to_short_term_memory(user1, "I have tomatoes", "Great!")
    memory_manager.add_to_short_term_memory(user2, "I have roses", "Wonderful!")
    
    # Check isolation
    history1 = memory_manager.get_short_term_memory(user1)
    history2 = memory_manager.get_short_term_memory(user2)
    
    assert "tomatoes" in str(history1).lower()
    assert "roses" in str(history2).lower()
    assert "roses" not in str(history1).lower()
    assert "tomatoes" not in str(history2).lower()

def test_plant_knowledge_retrieval(memory_manager):
    """Test RAG retrieval from plant knowledge base"""
    knowledge = memory_manager.get_plant_knowledge("tomato care")
    
    assert len(knowledge) > 0
    assert any(word in knowledge.lower() for word in ['tomato', 'water', 'sunlight'])

def test_clear_user_memory(memory_manager):
    """Test clearing user memory"""
    user_id = "test_clear_user"
    
    # Add some memory
    memory_manager.add_to_short_term_memory(user_id, "Test", "Response")
    
    # Clear
    memory_manager.clear_user_memory(user_id)
    
    # Check it's cleared
    history = memory_manager.get_short_term_memory(user_id)
    assert len(history) == 0

def test_get_user_plants(memory_manager):
    """Test extracting plants mentioned by user"""
    user_id = "test_plants_user"
    
    # Add conversations mentioning plants
    memory_manager.add_to_long_term_memory(
        user_id,
        "I have tomatoes and basil in my garden",
        "That's wonderful! Both are great plants."
    )
    
    plants = memory_manager.get_user_plants(user_id)
    
    # Should detect tomatoes and basil
    assert any('tomato' in plant.lower() for plant in plants) or \
           any('basil' in plant.lower() for plant in plants)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])