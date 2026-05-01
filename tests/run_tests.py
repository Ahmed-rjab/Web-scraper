"""
Test Runner - Run all unit tests
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_tests():
    """Discover and run all tests."""
    # Discover tests in the tests directory
    loader = unittest.TestLoader()
    start_dir = "tests"
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test modules
    test_modules = [
        "test_url_collector",
        "test_parser", 
        "test_analyzer",
        "test_database",
        "test_scraper"
    ]
    
    for module in test_modules:
        try:
            tests = loader.loadTestsFromName(f"tests.{module}")
            suite.addTests(tests)
        except Exception as e:
            print(f"Warning: Could not load {module}: {e}")
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())