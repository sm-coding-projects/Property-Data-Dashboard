"""
Simple rate limiting implementation for the Property Data Dashboard.
"""
import time
import logging
from collections import defaultdict, deque
from typing import Dict, Deque
from functools import wraps
from flask import request, jsonify


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
        self.logger = logging.getLogger(__name__)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request."""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) >= self.max_requests:
            self.logger.warning(f"Rate limit exceeded for client {client_id}")
            return False
        
        # Add current request
        client_requests.append(now)
        return True
    
    def get_client_id(self) -> str:
        """Get client identifier from request."""
        # Use IP address as client identifier
        return request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    def cleanup_old_entries(self):
        """Clean up old entries to prevent memory leaks."""
        now = time.time()
        cutoff = now - self.window_seconds
        
        clients_to_remove = []
        for client_id, requests in self.requests.items():
            # Remove old requests
            while requests and requests[0] <= cutoff:
                requests.popleft()
            
            # If no recent requests, mark for removal
            if not requests:
                clients_to_remove.append(client_id)
        
        # Remove empty client entries
        for client_id in clients_to_remove:
            del self.requests[client_id]


def rate_limit(limiter: RateLimiter):
    """Decorator to apply rate limiting to Flask routes."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = limiter.get_client_id()
            
            if not limiter.is_allowed(client_id):
                return jsonify({
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please wait before trying again.",
                        "retry_after": limiter.window_seconds
                    }
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Global rate limiter instance
rate_limiter = RateLimiter()