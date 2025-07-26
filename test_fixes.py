#!/usr/bin/env python3
"""
Test script to validate the key fixes implemented in the Property Data Dashboard.
"""
import os
import sys
import tempfile
import pandas as pd
from io import StringIO

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test configuration management."""
    print("Testing configuration management...")
    try:
        from config import config
        
        # Test basic configuration loading
        assert hasattr(config, 'DEBUG')
        assert hasattr(config, 'MAX_FILE_SIZE')
        assert hasattr(config, 'SESSION_TIMEOUT')
        
        # Test validation
        assert config.MAX_FILE_SIZE > 0
        assert config.SESSION_TIMEOUT > 0
        
        print("✓ Configuration management working correctly")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_error_handler():
    """Test error handling."""
    print("Testing error handling...")
    try:
        from error_handler import error_handler, ValidationError, ProcessingError
        
        # Test error handling
        error = ValidationError("Test validation error")
        response, status_code = error_handler.handle_validation_error(error)
        
        assert status_code == 400
        assert 'error' in response
        assert response['error']['code'] == 'VALIDATION_ERROR'
        
        print("✓ Error handling working correctly")
        return True
    except Exception as e:
        print(f"✗ Error handler test failed: {e}")
        return False

def test_file_processor():
    """Test file processing."""
    print("Testing file processing...")
    try:
        from file_processor import file_processor
        
        # Create a test CSV
        test_data = """Property ID,Property locality,Purchase price,Contract date,Property house number,Property street name,Primary purpose
1,Sydney,500000,2023-01-01,123,Main St,Residential
2,Melbourne,600000,2023-01-02,456,Oak Ave,Residential
3,Brisbane,400000,2023-01-03,789,Pine Rd,Commercial"""
        
        test_file = StringIO(test_data)
        result = file_processor.process_file(test_file, "test.csv")
        
        assert result.success == True
        assert result.data is not None
        assert len(result.data) == 3
        assert 'Property locality' in result.data.columns
        
        print("✓ File processing working correctly")
        return True
    except Exception as e:
        print(f"✗ File processor test failed: {e}")
        return False

def test_session_manager():
    """Test session management."""
    print("Testing session management...")
    try:
        from session_manager import create_session_manager
        
        # Create session manager
        session_manager = create_session_manager()
        
        # Test session creation
        test_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        session_id = session_manager.create_session(test_df)
        
        assert session_id is not None
        assert len(session_id) > 0
        
        # Test data retrieval
        retrieved_data = session_manager.get_data(session_id)
        assert retrieved_data is not None
        assert len(retrieved_data) == 3
        
        print("✓ Session management working correctly")
        return True
    except Exception as e:
        print(f"✗ Session manager test failed: {e}")
        return False

def test_rate_limiter():
    """Test rate limiting."""
    print("Testing rate limiting...")
    try:
        from rate_limiter import RateLimiter
        
        # Create rate limiter with low limits for testing
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        # Test normal requests
        assert limiter.is_allowed("test_client") == True
        assert limiter.is_allowed("test_client") == True
        
        # Test rate limiting
        assert limiter.is_allowed("test_client") == False
        
        print("✓ Rate limiting working correctly")
        return True
    except Exception as e:
        print(f"✗ Rate limiter test failed: {e}")
        return False

def test_security_fixes():
    """Test security fixes."""
    print("Testing security fixes...")
    try:
        from config import config
        
        # Test debug mode is configurable
        assert hasattr(config, 'DEBUG')
        
        # Test file size limits
        assert config.MAX_FILE_SIZE > 0
        
        # Test that production settings exist
        assert hasattr(config, 'is_production')
        
        print("✓ Security fixes working correctly")
        return True
    except Exception as e:
        print(f"✗ Security test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running Property Data Dashboard fix validation tests...\n")
    
    tests = [
        test_config,
        test_error_handler,
        test_file_processor,
        test_session_manager,
        test_rate_limiter,
        test_security_fixes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixes are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())