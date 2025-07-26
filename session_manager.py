"""
Session management system with configurable storage backends.
Supports in-memory storage for development and Redis for production.
"""
import json
import logging
import pickle
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd
from dataclasses import dataclass, asdict


@dataclass
class SessionData:
    """Session data container."""
    session_id: str
    data: pd.DataFrame
    created_at: datetime
    last_accessed: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'metadata': self.metadata,
            'data_shape': self.data.shape if self.data is not None else None,
            'data_columns': self.data.columns.tolist() if self.data is not None else None
        }


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def store(self, session_id: str, data: SessionData) -> None:
        """Store session data."""
        pass
    
    @abstractmethod
    def retrieve(self, session_id: str) -> Optional[SessionData]:
        """Retrieve session data."""
        pass
    
    @abstractmethod
    def delete(self, session_id: str) -> None:
        """Delete session data."""
        pass
    
    @abstractmethod
    def cleanup_expired(self, max_age: int) -> int:
        """Clean up expired sessions. Returns number of cleaned sessions."""
        pass
    
    @abstractmethod
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information without loading full data."""
        pass


class InMemoryStorage(StorageBackend):
    """In-memory storage backend for development."""
    
    def __init__(self):
        self._storage: Dict[str, SessionData] = {}
        self.logger = logging.getLogger(__name__)
    
    def store(self, session_id: str, data: SessionData) -> None:
        """Store session data in memory."""
        self._storage[session_id] = data
        self.logger.debug(f"Stored session {session_id} in memory")
    
    def retrieve(self, session_id: str) -> Optional[SessionData]:
        """Retrieve session data from memory."""
        session_data = self._storage.get(session_id)
        if session_data:
            # Update last accessed time
            session_data.last_accessed = datetime.utcnow()
            self.logger.debug(f"Retrieved session {session_id} from memory")
        return session_data
    
    def delete(self, session_id: str) -> None:
        """Delete session data from memory."""
        if session_id in self._storage:
            del self._storage[session_id]
            self.logger.debug(f"Deleted session {session_id} from memory")
    
    def cleanup_expired(self, max_age: int) -> int:
        """Clean up expired sessions from memory."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=max_age)
        expired_sessions = [
            sid for sid, data in self._storage.items()
            if data.last_accessed < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self._storage[session_id]
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions from memory")
        
        return len(expired_sessions)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information from memory."""
        session_data = self._storage.get(session_id)
        return session_data.to_dict() if session_data else None


class RedisStorage(StorageBackend):
    """Redis storage backend for production."""
    
    def __init__(self, redis_config: Dict[str, Any]):
        try:
            import redis
            self.redis_client = redis.Redis(**redis_config)
            self.redis_client.ping()  # Test connection
            self.logger = logging.getLogger(__name__)
            self.logger.info("Connected to Redis for session storage")
        except ImportError:
            raise ImportError("Redis package not installed. Install with: pip install redis")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")
    
    def _serialize_data(self, data: SessionData) -> bytes:
        """Serialize session data for Redis storage."""
        # Store DataFrame separately from metadata for efficiency
        serialized = {
            'session_id': data.session_id,
            'created_at': data.created_at.isoformat(),
            'last_accessed': data.last_accessed.isoformat(),
            'metadata': data.metadata,
            'dataframe': pickle.dumps(data.data) if data.data is not None else None
        }
        return pickle.dumps(serialized)
    
    def _deserialize_data(self, serialized: bytes) -> SessionData:
        """Deserialize session data from Redis storage."""
        data_dict = pickle.loads(serialized)
        
        return SessionData(
            session_id=data_dict['session_id'],
            data=pickle.loads(data_dict['dataframe']) if data_dict['dataframe'] else None,
            created_at=datetime.fromisoformat(data_dict['created_at']),
            last_accessed=datetime.fromisoformat(data_dict['last_accessed']),
            metadata=data_dict['metadata']
        )
    
    def store(self, session_id: str, data: SessionData, ttl: int = 3600) -> None:
        """Store session data in Redis with TTL."""
        try:
            serialized_data = self._serialize_data(data)
            self.redis_client.setex(f"session:{session_id}", ttl, serialized_data)
            
            # Store session info separately for quick access
            info_key = f"session_info:{session_id}"
            self.redis_client.setex(info_key, ttl, json.dumps(data.to_dict()))
            
            self.logger.debug(f"Stored session {session_id} in Redis with TTL {ttl}")
        except Exception as e:
            self.logger.error(f"Failed to store session {session_id} in Redis: {str(e)}")
            raise
    
    def retrieve(self, session_id: str) -> Optional[SessionData]:
        """Retrieve session data from Redis."""
        try:
            serialized_data = self.redis_client.get(f"session:{session_id}")
            if not serialized_data:
                return None
            
            session_data = self._deserialize_data(serialized_data)
            
            # Update last accessed time
            session_data.last_accessed = datetime.utcnow()
            self.store(session_id, session_data)  # Update in Redis
            
            self.logger.debug(f"Retrieved session {session_id} from Redis")
            return session_data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve session {session_id} from Redis: {str(e)}")
            return None
    
    def delete(self, session_id: str) -> None:
        """Delete session data from Redis."""
        try:
            self.redis_client.delete(f"session:{session_id}")
            self.redis_client.delete(f"session_info:{session_id}")
            self.logger.debug(f"Deleted session {session_id} from Redis")
        except Exception as e:
            self.logger.error(f"Failed to delete session {session_id} from Redis: {str(e)}")
    
    def cleanup_expired(self, max_age: int) -> int:
        """Clean up expired sessions from Redis (handled automatically by TTL)."""
        # Redis handles expiration automatically with TTL
        # This method is for compatibility with the interface
        return 0
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information from Redis."""
        try:
            info_data = self.redis_client.get(f"session_info:{session_id}")
            if info_data:
                return json.loads(info_data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get session info {session_id} from Redis: {str(e)}")
            return None


class SessionManager:
    """Session manager with configurable storage backend."""
    
    def __init__(self, storage_backend: StorageBackend, session_timeout: int = 3600):
        self.storage = storage_backend
        self.session_timeout = session_timeout
        self.logger = logging.getLogger(__name__)
    
    def create_session(self, data: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new session with data."""
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session_data = SessionData(
            session_id=session_id,
            data=data,
            created_at=now,
            last_accessed=now,
            metadata=metadata or {}
        )
        
        self.storage.store(session_id, session_data)
        self.logger.info(f"Created session {session_id} with {len(data)} rows")
        
        return session_id
    
    def get_data(self, session_id: str) -> Optional[pd.DataFrame]:
        """Get data for a session."""
        session_data = self.storage.retrieve(session_id)
        if session_data:
            return session_data.data
        return None
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information without loading full data."""
        return self.storage.get_session_info(session_id)
    
    def update_session_data(self, session_id: str, data: pd.DataFrame) -> bool:
        """Update data for an existing session."""
        session_data = self.storage.retrieve(session_id)
        if session_data:
            session_data.data = data
            session_data.last_accessed = datetime.utcnow()
            self.storage.store(session_id, session_data)
            return True
        return False
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        self.storage.delete(session_id)
        self.logger.info(f"Deleted session {session_id}")
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        cleaned_count = self.storage.cleanup_expired(self.session_timeout)
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} expired sessions")
        return cleaned_count
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        return self.storage.get_session_info(session_id) is not None


def create_session_manager(redis_config: Optional[Dict[str, Any]] = None, 
                          session_timeout: int = 3600) -> SessionManager:
    """Factory function to create session manager with appropriate backend."""
    if redis_config:
        try:
            storage = RedisStorage(redis_config)
            logging.getLogger(__name__).info("Using Redis storage backend")
        except (ImportError, ConnectionError) as e:
            logging.getLogger(__name__).warning(f"Redis unavailable, falling back to memory: {str(e)}")
            storage = InMemoryStorage()
    else:
        storage = InMemoryStorage()
        logging.getLogger(__name__).info("Using in-memory storage backend")
    
    return SessionManager(storage, session_timeout)