"""
Memory Management System
Implements both short-term (conversation buffer) and long-term (ChromaDB) memory per user
"""
import os
import logging
from typing import List, Dict
from collections import defaultdict
from langchain_core.messages import HumanMessage, AIMessage
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages per-user short-term and long-term memory"""
    
    def __init__(self):
        # Short-term memory: per-user conversation buffer
        self.short_term_memory: Dict[str, List] = defaultdict(list)
        self.max_short_term = 10  # Keep last 10 messages per user
        
        # Long-term memory: ChromaDB
        chroma_path = os.getenv('CHROMA_DB_PATH', './data/chroma')
        os.makedirs(chroma_path, exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Create or get collections
        self.memory_collection = self.chroma_client.get_or_create_collection(
            name=os.getenv('CHROMA_COLLECTION', 'garden_memory'),
            metadata={"description": "Long-term user conversations and context"}
        )
        
        self.plant_collection = self.chroma_client.get_or_create_collection(
            name="plant_knowledge",
            metadata={"description": "Plant care knowledge base"}
        )
        
        # Initialize plant knowledge
        self._initialize_plant_knowledge()
        
        logger.info("Memory Manager initialized")
    
    def _initialize_plant_knowledge(self):
        """Load plant knowledge into ChromaDB for RAG"""
        import json
        
        plants_file = './data/plants_info.json'
        
        # Create default plant knowledge if not exists
        if not os.path.exists(plants_file):
            os.makedirs('./data', exist_ok=True)
            default_plants = [
                {
                    "name": "Tomato",
                    "water_frequency": "Every 2-3 days",
                    "sunlight": "6-8 hours daily",
                    "soil": "Well-draining, pH 6.0-6.8",
                    "tips": "Support with stakes, prune suckers regularly"
                },
                {
                    "name": "Basil",
                    "water_frequency": "Daily in hot weather",
                    "sunlight": "6 hours daily",
                    "soil": "Rich, moist, well-draining",
                    "tips": "Pinch flowers to encourage leaf growth"
                },
                {
                    "name": "Rose",
                    "water_frequency": "2-3 times per week",
                    "sunlight": "6+ hours daily",
                    "soil": "Loamy, pH 6.0-7.0",
                    "tips": "Deadhead spent blooms, fertilize monthly"
                },
                {
                    "name": "Cactus",
                    "water_frequency": "Every 2-3 weeks",
                    "sunlight": "Bright indirect light",
                    "soil": "Sandy, well-draining cactus mix",
                    "tips": "Avoid overwatering, ensure drainage holes"
                },
                {
                    "name": "Orchid",
                    "water_frequency": "Once a week",
                    "sunlight": "Bright indirect light",
                    "soil": "Bark-based orchid mix",
                    "tips": "Mist leaves, avoid water on flowers"
                }
            ]
            
            with open(plants_file, 'w') as f:
                json.dump(default_plants, f, indent=2)
        
        # Load and index plants
        try:
            with open(plants_file, 'r') as f:
                plants = json.load(f)
            
            # Check if already indexed
            existing = self.plant_collection.get()
            if len(existing['ids']) > 0:
                logger.info(f"Plant knowledge already indexed: {len(existing['ids'])} plants")
                return
            
            # Index plants
            for plant in plants:
                doc_text = f"{plant['name']}: Water {plant['water_frequency']}, " \
                          f"Sunlight: {plant['sunlight']}, Soil: {plant['soil']}, " \
                          f"Tips: {plant['tips']}"
                
                self.plant_collection.add(
                    documents=[doc_text],
                    metadatas=[{"plant_name": plant['name']}],
                    ids=[f"plant_{plant['name'].lower()}"]
                )
            
            logger.info(f"Indexed {len(plants)} plants into knowledge base")
        except Exception as e:
            logger.error(f"Failed to initialize plant knowledge: {e}")
    
    def get_short_term_memory(self, user_id: str) -> List:
        """Get conversation history for user (short-term memory)"""
        return self.short_term_memory.get(user_id, [])[-self.max_short_term:]
    
    def add_to_short_term_memory(self, user_id: str, user_msg: str, ai_msg: str):
        """Add conversation turn to short-term memory"""
        self.short_term_memory[user_id].append(HumanMessage(content=user_msg))
        self.short_term_memory[user_id].append(AIMessage(content=ai_msg))
        
        # Keep only recent messages
        if len(self.short_term_memory[user_id]) > self.max_short_term * 2:
            self.short_term_memory[user_id] = self.short_term_memory[user_id][-self.max_short_term * 2:]
        
        logger.debug(f"Added to short-term memory for user {user_id}")
    
    def add_to_long_term_memory(self, user_id: str, user_msg: str, ai_msg: str):
        """Add conversation to long-term memory (ChromaDB)"""
        try:
            doc_text = f"User: {user_msg}\nAssistant: {ai_msg}"
            doc_id = f"{user_id}_{len(self.memory_collection.get(where={'user_id': user_id})['ids'])}"
            
            self.memory_collection.add(
                documents=[doc_text],
                metadatas=[{"user_id": user_id}],
                ids=[doc_id]
            )
            
            logger.debug(f"Added to long-term memory for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to add to long-term memory: {e}")
    
    def get_relevant_long_term_memory(self, user_id: str, query: str, n_results: int = 3) -> str:
        """Retrieve relevant past conversations (RAG from long-term memory)"""
        try:
            results = self.memory_collection.query(
                query_texts=[query],
                where={"user_id": user_id},
                n_results=n_results
            )
            
            if results['documents'] and results['documents'][0]:
                context = "\n\n".join(results['documents'][0])
                logger.debug(f"Retrieved {len(results['documents'][0])} relevant memories")
                return context
        except Exception as e:
            logger.error(f"Failed to retrieve long-term memory: {e}")
        
        return ""
    
    def get_plant_knowledge(self, query: str, n_results: int = 2) -> str:
        """Retrieve plant care knowledge (RAG)"""
        try:
            results = self.plant_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if results['documents'] and results['documents'][0]:
                knowledge = "\n\n".join(results['documents'][0])
                logger.debug(f"Retrieved plant knowledge: {knowledge[:100]}")
                return knowledge
        except Exception as e:
            logger.error(f"Failed to retrieve plant knowledge: {e}")
        
        return ""
    
    def get_user_plants(self, user_id: str) -> List[str]:
        """Extract list of plants mentioned by user"""
        try:
            # Query user's memories for plant mentions
            results = self.memory_collection.get(
                where={"user_id": user_id}
            )
            
            plants = set()
            plant_keywords = ['tomato', 'basil', 'rose', 'cactus', 'orchid', 'mint', 'lettuce']
            
            for doc in results['documents']:
                doc_lower = doc.lower()
                for plant in plant_keywords:
                    if plant in doc_lower:
                        plants.add(plant.capitalize())
            
            return list(plants)
        except Exception as e:
            logger.error(f"Failed to get user plants: {e}")
            return []
    
    def get_all_user_ids(self) -> List[str]:
        """Get all user IDs that have stored data in ChromaDB or short-term memory"""
        try:
            user_ids = set()
            
            # Get from short-term memory
            user_ids.update(self.short_term_memory.keys())
            
            # Get from ChromaDB long-term memory
            results = self.memory_collection.get()
            for metadata in results.get('metadatas', []):
                if 'user_id' in metadata:
                    user_ids.add(metadata['user_id'])
            
            logger.debug(f"Found {len(user_ids)} unique users")
            return list(user_ids)
        except Exception as e:
            logger.error(f"Error getting all user IDs: {e}")
            return []
    
    def clear_user_memory(self, user_id: str):
        """Clear all memory for a user"""
        self.short_term_memory.pop(user_id, None)
        
        try:
            # Clear from ChromaDB
            results = self.memory_collection.get(where={"user_id": user_id})
            if results['ids']:
                self.memory_collection.delete(ids=results['ids'])
            
            logger.info(f"Cleared memory for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to clear user memory: {e}")