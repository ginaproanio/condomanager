import unittest
from app import create_app
from app.extensions import limiter

class TestRateLimiting(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['RATELIMIT_ENABLED'] = True
        self.app.config['RATELIMIT_STORAGE_URI'] = 'memory://'
        self.client = self.app.test_client()
        
        # Ensure we start fresh
        with self.app.app_context():
            if hasattr(limiter, 'reset'):
                limiter.reset()

    def test_login_rate_limit(self):
        """Test that login endpoint is limited to 5 per minute"""
        # Make 5 calls (status doesn't matter for rate limit, usually hits are counted)
        # Note: We send empty json to avoid actual login logic overhead, 
        # but rate limit should trigger before validation if configured 'before_request'
        # or inside route decorator.
        
        # We need to use a unique IP for this test to avoid conflicts with other tests if persistent
        # but memory storage is per-process/app usually.
        
        # Hit the limit (5 allowed)
        for i in range(5):
            response = self.client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'wrong'
            })
            # 400 is fine (missing fields), as long as it's not 429
            self.assertNotEqual(response.status_code, 429, f"Request {i+1} should not be rate limited")
        
        # The 6th call should be blocked
        response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrong'
        })
        
        self.assertEqual(response.status_code, 429, "Request 6 should be rate limited (5/minute)")
        self.assertIn(b'Has excedido el l', response.data)

if __name__ == '__main__':
    unittest.main()

