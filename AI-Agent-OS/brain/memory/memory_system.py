"""3-Tier Memory System - Cache, Context, Vector DB"""
import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
import hashlib

logger = logging.getLogger(__name__)


class MemoryCache:
    """
    Tier 1: In-memory cache (5-minute TTL)
    For frequently accessed data
    """
    
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._data: Dict[str, tuple] = {}
        self._access_count: Dict[str, int] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        if key not in self._data:
            return None
        
        data, timestamp = self._data[key]
        
        if time.time() - timestamp > self.ttl:
            del self._data[key]
            return None
        
        self._access_count[key] = self._access_count.get(key, 0) + 1
        return data
    
    async def set(self, key: str, data: Any):
        """Set in cache"""
        self._data[key] = (data, time.time())
    
    async def clear(self):
        """Clear cache"""
        self._data.clear()


class ContextMemory:
    """
    Tier 2: Context/Session memory
    For current task context (survives one session)
    """
    
    def __init__(self):
        self._context: Dict[str, Any] = {}
        self._session_id = None
        self._lock = asyncio.Lock()
    
    async def init_session(self, session_id: str):
        """Initialize new session"""
        async with self._lock:
            self._session_id = session_id
            self._context = {
                "session_id": session_id,
                "created_at": time.time(),
                "messages": [],
                "variables": {}
            }
    
    async def add_message(self, role: str, content: str):
        """Add message to context"""
        async with self._lock:
            if "messages" not in self._context:
                self._context["messages"] = []
            
            self._context["messages"].append({
                "role": role,
                "content": content,
                "timestamp": time.time()
            })
            
            # Keep last 20 messages
            if len(self._context["messages"]) > 20:
                self._context["messages"] = self._context["messages"][-20:]
    
    async def set_variable(self, key: str, value: Any):
        """Set context variable"""
        async with self._lock:
            self._context["variables"][key] = value
    
    async def get_context(self) -> Dict:
        """Get full context"""
        async with self._lock:
            return self._context.copy()
    
    async def clear_session(self):
        """Clear current session"""
        async with self._lock:
            self._context = {}
            self._session_id = None


class VectorMemory:
    """
    Tier 3: Long-term vector memory
    For semantic search using embeddings
    """
    
    def __init__(self):
        self._vectors: Dict[str, Dict] = {}
        self._embedder = None
        self._lock = asyncio.Lock()
        self._init_embedder()
    
    def _init_embedder(self):
        """Initialize embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence transformer...")
            self._embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            logger.warning("SentenceTransformer not installed, using mock embedder")
            self._embedder = None
    
    async def store(self, key: str, text: str, metadata: Dict = None):
        """Store text with embedding"""
        async with self._lock:
            if self._embedder:
                embedding = self._embedder.encode(text).tolist()
            else:
                # Mock embedding
                embedding = [float(ord(c)) / 127 for c in text[:384]]
            
            self._vectors[key] = {
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {},
                "timestamp": time.time()
            }
    
    async def search(self, query: str, top_k: int = 5) -> List[tuple]:
        """Search similar memories by semantic similarity"""
        if not self._embedder:
            return []
        
        async with self._lock:
            query_embedding = self._embedder.encode(query).tolist()
            
            # Calculate similarity with all stored vectors
            similarities = []
            for key, vector_data in self._vectors.items():
                similarity = self._cosine_similarity(
                    query_embedding,
                    vector_data["embedding"]
                )
                similarities.append((key, similarity, vector_data["text"]))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
    
    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity"""
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = sum(x ** 2 for x in a) ** 0.5
        magnitude_b = sum(y ** 2 for y in b) ** 0.5
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0
        
        return dot_product / (magnitude_a * magnitude_b)
    
    async def clear(self):
        """Clear vector memory"""
        async with self._lock:
            self._vectors.clear()


class MemorySystem:
    """Unified 3-tier memory interface"""
    
    def __init__(self):
        self.cache = MemoryCache(ttl=300)
        self.context = ContextMemory()
        self.vectors = VectorMemory()
    
    async def initialize(self, session_id: str):
        """Initialize memory system for session"""
        await self.context.init_session(session_id)
        logger.info(f"Memory system initialized for session {session_id}")
    
    async def cleanup(self):
        """Cleanup all tiers"""
        await self.cache.clear()
        await self.context.clear_session()
        await self.vectors.clear()
