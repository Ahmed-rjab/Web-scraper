"""
Unit Tests for Database Component
"""
import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database


class TestDatabase(unittest.TestCase):
    """Test cases for database module."""
    
    def setUp(self):
        """Create a temporary database for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
    
    def tearDown(self):
        """Clean up temporary database."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_database(self):
        """Test database initialization."""
        database.init_database(self.db_path)
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_store_result(self):
        """Test storing a result."""
        database.init_database(self.db_path)
        
        url_id = database.store_result(
            url="http://test-phish.com",
            status_code=200,
            indicators=[
                {"indicator": "password_field", "score": 2, "detail": "Test detail"}
            ],
            total_score=2,
            risk_level="LOW",
            db_path=self.db_path
        )
        
        self.assertIsInstance(url_id, int)
        self.assertGreater(url_id, 0)
    
    def test_get_all_results(self):
        """Test retrieving all results."""
        database.init_database(self.db_path)
        
        # Store test data
        database.store_result(
            url="http://test1.com",
            status_code=200,
            indicators=[{"indicator": "test", "score": 1, "detail": "test"}],
            total_score=1,
            risk_level="LOW",
            db_path=self.db_path
        )
        
        results = database.get_all_results(db_path=self.db_path)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
    
    def test_get_result_by_id(self):
        """Test retrieving a specific result by ID."""
        database.init_database(self.db_path)
        
        url_id = database.store_result(
            url="http://test.com",
            status_code=200,
            indicators=[
                {"indicator": "password_field", "score": 2, "detail": "Found password"}
            ],
            total_score=2,
            risk_level="LOW",
            db_path=self.db_path
        )
        
        result = database.get_result_by_id(url_id, self.db_path)
        self.assertIsNotNone(result)
        self.assertEqual(result["url"], "http://test.com")
        self.assertEqual(len(result["indicators"]), 1)
    
    def test_filter_by_risk_level(self):
        """Test filtering results by risk level."""
        database.init_database(self.db_path)
        
        # Store different risk levels
        database.store_result(
            url="http://high.com",
            status_code=200,
            indicators=[{"indicator": "test", "score": 8, "detail": ""}],
            total_score=8,
            risk_level="HIGH",
            db_path=self.db_path
        )
        database.store_result(
            url="http://low.com",
            status_code=200,
            indicators=[{"indicator": "test", "score": 1, "detail": ""}],
            total_score=1,
            risk_level="LOW",
            db_path=self.db_path
        )
        
        high_results = database.get_all_results(
            risk_level="HIGH", 
            db_path=self.db_path
        )
        self.assertEqual(len(high_results), 1)
        self.assertEqual(high_results[0]["risk_level"], "HIGH")
    
    def test_get_statistics(self):
        """Test getting statistics."""
        database.init_database(self.db_path)
        
        # Store test data
        database.store_result(
            url="http://test.com",
            status_code=200,
            indicators=[{"indicator": "test", "score": 5, "detail": ""}],
            total_score=5,
            risk_level="MEDIUM",
            db_path=self.db_path
        )
        
        stats = database.get_statistics(self.db_path)
        self.assertIn("total_urls", stats)
        self.assertIn("high_count", stats)
        self.assertIn("medium_count", stats)
        self.assertIn("low_count", stats)
        self.assertIn("average_score", stats)
        self.assertEqual(stats["total_urls"], 1)
    
    def test_export_to_csv(self):
        """Test CSV export."""
        database.init_database(self.db_path)
        
        database.store_result(
            url="http://test.com",
            status_code=200,
            indicators=[{"indicator": "test", "score": 1, "detail": ""}],
            total_score=1,
            risk_level="LOW",
            db_path=self.db_path
        )
        
        csv_path = os.path.join(self.temp_dir, "export.csv")
        database.export_to_csv(csv_path, self.db_path)
        
        self.assertTrue(os.path.exists(csv_path))
        
        # Check CSV content
        with open(csv_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("http://test.com", content)


if __name__ == "__main__":
    unittest.main()