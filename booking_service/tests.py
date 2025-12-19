import unittest
import json
from app import app

class BookingServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        """Test if the service is up and running"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)

    def test_login_page_load(self):
        """Test if login endpoint accepts OPTIONS (CORS check)"""
        response = self.app.open('/login', method='OPTIONS')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()