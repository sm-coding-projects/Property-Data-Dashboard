"""
Enhanced error handling and logging for the Property Data Dashboard.
Provides centralized error management with user-friendly messages.
"""
import logging
import traceback
from datetime import datetime
from typing import Tuple, Dict, Any, Optional
from flask import jsonify


class ErrorHandler:
    """Centralized error handling with logging and user-friendly messages."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_upload_error(self, error: Exception, context: Optional[Dict] = None) -> Tuple[Dict, int]:
        """Handle file upload related errors."""
        error_code, user_message, status_code = self._classify_upload_error(error)
        
        self._log_error(error, error_code, context or {})
        
        return self._create_error_response(error_code, user_message), status_code
    
    def handle_processing_error(self, error: Exception, context: Optional[Dict] = None) -> Tuple[Dict, int]:
        """Handle data processing related errors."""
        error_code, user_message, status_code = self._classify_processing_error(error)
        
        self._log_error(error, error_code, context or {})
        
        return self._create_error_response(error_code, user_message), status_code
    
    def handle_validation_error(self, error: Exception, context: Optional[Dict] = None) -> Tuple[Dict, int]:
        """Handle input validation errors."""
        error_code = "VALIDATION_ERROR"
        user_message = f"Invalid input: {str(error)}"
        status_code = 400
        
        self._log_error(error, error_code, context or {}, level=logging.WARNING)
        
        return self._create_error_response(error_code, user_message), status_code
    
    def handle_rate_limit_error(self, context: Optional[Dict] = None) -> Tuple[Dict, int]:
        """Handle rate limiting errors."""
        error_code = "RATE_LIMIT_EXCEEDED"
        user_message = "Too many requests. Please wait before trying again."
        status_code = 429
        
        self.logger.warning(f"Rate limit exceeded: {context or {}}")
        
        return self._create_error_response(error_code, user_message), status_code
    
    def handle_generic_error(self, error: Exception, context: Optional[Dict] = None) -> Tuple[Dict, int]:
        """Handle generic/unexpected errors."""
        error_code = "INTERNAL_ERROR"
        user_message = "An unexpected error occurred. Please try again later."
        status_code = 500
        
        self._log_error(error, error_code, context or {}, level=logging.ERROR)
        
        return self._create_error_response(error_code, user_message), status_code
    
    def _classify_upload_error(self, error: Exception) -> Tuple[str, str, int]:
        """Classify upload-related errors."""
        error_str = str(error).lower()
        
        if "no file" in error_str or "empty" in error_str:
            return "NO_FILE", "No file was uploaded. Please select a CSV file.", 400
        
        if "file too large" in error_str or "size" in error_str:
            return "FILE_TOO_LARGE", "File is too large. Maximum size is 500MB.", 413
        
        if "encoding" in error_str or "decode" in error_str:
            return "ENCODING_ERROR", "File encoding not supported. Please use UTF-8 or Latin-1.", 400
        
        if "csv" in error_str or "format" in error_str:
            return "INVALID_FORMAT", "Invalid file format. Please upload a valid CSV file.", 400
        
        if "memory" in error_str or "out of memory" in error_str:
            return "MEMORY_ERROR", "File is too large to process. Please try a smaller file.", 413
        
        return "UPLOAD_ERROR", "Failed to upload file. Please check the file format and try again.", 400
    
    def _classify_processing_error(self, error: Exception) -> Tuple[str, str, int]:
        """Classify data processing errors."""
        error_str = str(error).lower()
        
        if "column" in error_str or "missing" in error_str:
            return "MISSING_COLUMNS", "Required columns are missing from the CSV file.", 400
        
        if "data type" in error_str or "conversion" in error_str:
            return "DATA_TYPE_ERROR", "Invalid data types in CSV file. Please check your data.", 400
        
        if "empty" in error_str or "no data" in error_str:
            return "EMPTY_DATA", "No valid data found in the uploaded file.", 400
        
        if "memory" in error_str:
            return "MEMORY_ERROR", "Insufficient memory to process this file.", 500
        
        if "timeout" in error_str:
            return "TIMEOUT_ERROR", "Processing timed out. Please try a smaller file.", 408
        
        return "PROCESSING_ERROR", "Failed to process data. Please check your file format.", 500
    
    def _log_error(self, error: Exception, error_code: str, context: Dict, level: int = logging.ERROR):
        """Log error with context information."""
        log_data = {
            'error_code': error_code,
            'error_message': str(error),
            'error_type': type(error).__name__,
            'timestamp': datetime.utcnow().isoformat(),
            'context': context
        }
        
        # Add stack trace for server errors
        if level >= logging.ERROR:
            log_data['stack_trace'] = traceback.format_exc()
        
        self.logger.log(level, f"Error occurred: {log_data}")
    
    def _create_error_response(self, error_code: str, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "error": {
                "code": error_code,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class ProcessingError(Exception):
    """Custom exception for data processing errors."""
    pass


class RateLimitError(Exception):
    """Custom exception for rate limiting errors."""
    pass


# Global error handler instance
error_handler = ErrorHandler()