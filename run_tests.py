#!/usr/bin/env python3
"""
Simple test runner script for the MCP Client tests.
Run this script to execute all tests with proper environment setup.
"""

import os
import sys
import unittest

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def load_environment():
    """Load environment variables from .env file if it exists"""
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        print("Loading environment variables from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"Set {key.strip()}")
    else:
        print("⚠️  No .env file found. Make sure GEMINI_API_KEY is set for integration tests.")

def run_tests():
    """Run all tests in the tests directory"""
    print("=" * 60)
    print("Running MCP Client Tests")
    print("=" * 60)
    
    # Load environment variables
    load_environment()
    
    # Check if API key is available for integration tests
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"API key found (ends with: ...{api_key[-4:]})") 
        print("Integration tests will run")
    else:
        print("WARNING: No API key found - integration tests will be skipped")
    
    print("-" * 60)    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("-" * 60)
    if result.wasSuccessful():
        print("SUCCESS: All tests passed!")
    else:
        print("ERROR: Some tests failed.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)