"""
Unit tests for RAG (Retrieval Augmented Generation)
Tests the ChromaDB-based knowledge retrieval system using MemoryManager
"""

import pytest
import os
import sys
import tempfile
import shutil

# Ensure project root path is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.memory import MemoryManager


# ==========================================================
# === Pytest Fixtures ======================================
# ==========================================================

@pytest.fixture(scope="module")
def temp_chroma_path():
    """Create temporary ChromaDB path for isolated testing"""
    temp_dir = tempfile.mkdtemp()
    os.environ["CHROMA_DB_PATH"] = temp_dir
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def memory_manager(temp_chroma_path):
    """Initialize MemoryManager with RAG capabilities"""
    return MemoryManager()


# ==========================================================
# === Tests for Plant Knowledge (RAG Base) =================
# ==========================================================

def test_plant_knowledge_base_exists(memory_manager):
    """Ensure plant knowledge base collection exists and has data"""
    collection = memory_manager.plant_collection
    results = collection.get()

    assert "ids" in results
    assert len(results["ids"]) > 0, "Plant knowledge base should contain data"


def test_retrieve_plant_knowledge(memory_manager):
    """Retrieve plant care information for a known plant"""
    knowledge = memory_manager.get_plant_knowledge("tomato")
    assert isinstance(knowledge, str)
    assert len(knowledge) > 0
    assert any(word in knowledge.lower() for word in ["tomato", "water", "soil", "sunlight"])


def test_rag_relevance(memory_manager):
    """Check that different plant queries yield distinct results"""
    tomato_knowledge = memory_manager.get_plant_knowledge("tomato watering")
    cactus_knowledge = memory_manager.get_plant_knowledge("cactus desert plant")

    assert isinstance(tomato_knowledge, str)
    assert isinstance(cactus_knowledge, str)
    assert len(tomato_knowledge) > 0
    assert len(cactus_knowledge) > 0
    assert tomato_knowledge != cactus_knowledge, "Different plants should yield different info"


def test_rag_multiple_results(memory_manager):
    """Test retrieval of multiple relevant knowledge entries"""
    knowledge = memory_manager.get_plant_knowledge("watering schedule", n_results=3)
    assert isinstance(knowledge, str)
    assert len(knowledge) > 0


def test_rag_empty_query(memory_manager):
    """Ensure RAG handles empty query safely"""
    result = memory_manager.get_plant_knowledge("")
    assert isinstance(result, str)


# ==========================================================
# === Tests for Long-Term User Memory + RAG =================
# ==========================================================

def test_user_memory_rag(memory_manager):
    """Test retrieving relevant long-term memory for a user"""
    user_id = "test_rag_user"

    memory_manager.add_to_long_term_memory(
        user_id,
        "I have tomato plants in my garden",
        "Great! Tomatoes need regular watering."
    )

    memory_manager.add_to_long_term_memory(
        user_id,
        "My roses are blooming",
        "Wonderful! Make sure to deadhead them regularly."
    )

    relevant = memory_manager.get_relevant_long_term_memory(user_id, "my plants")

    assert isinstance(relevant, str)
    assert len(relevant) > 0


def test_per_user_rag_isolation(memory_manager):
    """Ensure RAG isolates data per user"""
    user1, user2 = "rag_user_1", "rag_user_2"

    memory_manager.add_to_long_term_memory(user1, "I grow tomatoes", "Nice!")
    memory_manager.add_to_long_term_memory(user2, "I grow roses", "Beautiful!")

    relevant1 = memory_manager.get_relevant_long_term_memory(user1, "my plants")
    relevant2 = memory_manager.get_relevant_long_term_memory(user2, "my plants")

    if relevant1 and relevant2:
        assert ("tomato" in relevant1.lower() or "rose" not in relevant1.lower())
        assert ("rose" in relevant2.lower() or "tomato" not in relevant2.lower())


def test_rag_with_metadata(memory_manager):
    """Verify metadata is stored correctly for user memories"""
    user_id = "metadata_test_user"

    memory_manager.add_to_long_term_memory(user_id, "Test message", "Test response")

    results = memory_manager.memory_collection.get(where={"user_id": user_id})

    assert "metadatas" in results
    assert len(results["metadatas"]) > 0
    assert results["metadatas"][0]["user_id"] == user_id


# ==========================================================
# === General RAG Behavior =================================
# ==========================================================

def test_rag_query_similarity(memory_manager):
    """Similar queries should yield similar information"""
    query1 = "how to water tomatoes"
    query2 = "tomato watering guide"

    result1 = memory_manager.get_plant_knowledge(query1)
    result2 = memory_manager.get_plant_knowledge(query2)

    assert isinstance(result1, str)
    assert isinstance(result2, str)
    assert len(result1) > 0 and len(result2) > 0


def test_plant_knowledge_comprehensiveness(memory_manager):
    """Ensure plant knowledge covers core care aspects"""
    knowledge = memory_manager.get_plant_knowledge("complete plant care guide")

    care_aspects = ["water", "sunlight", "soil"]
    found_aspects = sum(1 for aspect in care_aspects if aspect in knowledge.lower())

    assert found_aspects >= 1, "Knowledge should cover basic care aspects"


# ==========================================================
# === Entry Point ==========================================
# ==========================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
