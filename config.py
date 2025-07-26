"""
Configuration management for the Property Data Dashboard.
Handles environment-specific settings and validation.
"""
import os
import logging
from typing import Optional


class Config:
    """Application configuration with environment variable support."""
    
    def __init__(self):
        # Security settings
        self.DEBUG = self._get_bool('DEBUG', False)
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
        
        # File processing settings
        self.MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '500')) * 1024 * 1024  # MB to bytes
        self.ALLOWED_EXTENSIONS = {'csv'}
        self.UPLOAD_TIMEOUT = int(os.getenv('UPLOAD_TIMEOUT', '300'))  # seconds
        
        # Session and storage settings
        self.REDIS_URL = os.getenv('REDIS_URL', None)
        self.SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))  # seconds
        self.USE_REDIS = self.REDIS_URL is not None
        
        # Logging settings
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.LOG_FILE = os.getenv('LOG_FILE', None)
        self.LOG_FORMAT = os.getenv('LOG_FORMAT', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Performance settings
        self.CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))  # seconds
        self.MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
        self.WORKER_TIMEOUT = int(os.getenv('WORKER_TIMEOUT', '600'))  # seconds
        
        # Rate limiting
        self.RATE_LIMIT_ENABLED = self._get_bool('RATE_LIMIT_ENABLED', True)
        self.RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
        self.RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # seconds
        
        # Data processing settings
        self.CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '10000'))  # rows
        self.MAX_MEMORY_USAGE = int(os.getenv('MAX_MEMORY_USAGE', '1024'))  # MB
        
        # Validate configuration
        self._validate_config()
    
    def _get_bool(self, key: str, default: bool) -> bool:
        """Convert environment variable to boolean."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _validate_config(self):
        """Validate configuration values."""
        if self.DEBUG and os.getenv('FLASK_ENV') == 'production':
            raise ValueError("DEBUG mode cannot be enabled in production")
        
        if self.MAX_FILE_SIZE <= 0:
            raise ValueError("MAX_FILE_SIZE must be positive")
        
        if self.SESSION_TIMEOUT <= 0:
            raise ValueError("SESSION_TIMEOUT must be positive")
        
        if self.LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError(f"Invalid LOG_LEVEL: {self.LOG_LEVEL}")
    
    def setup_logging(self):
        """Configure application logging."""
        log_level = getattr(logging, self.LOG_LEVEL)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format=self.LOG_FORMAT,
            filename=self.LOG_FILE
        )
        
        # Create console handler if no log file specified
        if not self.LOG_FILE:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            formatter = logging.Formatter(self.LOG_FORMAT)
            console_handler.setFormatter(formatter)
            
            # Add to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(console_handler)
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return os.getenv('FLASK_ENV') == 'production' or not self.DEBUG
    
    def get_redis_config(self) -> Optional[dict]:
        """Get Redis configuration if available."""
        if not self.USE_REDIS:
            return None
        
        return {
            'url': self.REDIS_URL,
            'decode_responses': True,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'retry_on_timeout': True
        }


# Global configuration instance
config = Config()