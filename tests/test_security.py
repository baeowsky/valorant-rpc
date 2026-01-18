from src.webserver.server import app
from src.webserver import server
import unittest
import logging

# Disable Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class MockClient:
    region = "na"
    puuid = "test_puuid"

    def party_join(self, party_id):
        # Mock response
        return {"data": "mock_join"}

    def party_request_to_join(self, party_id, friend_id):
        return {"Requests": []}

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        server.client = MockClient()

    def test_xss_in_region_join(self):
        payload = "<script>alert('XSS')</script>"
        # Send a region that doesn't match 'na' to trigger the error message
        response = self.app.get(f'/valorant/join/1234?region={payload}')

        content = response.get_data(as_text=True)
        print(f"\nResponse content: {content}")

        # The payload should be escaped now
        escaped_payload = "&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;"

        if payload not in content:
            print("SUCCESS: XSS payload NOT found in response.")
        else:
            print("FAILURE: XSS payload FOUND in response.")

        self.assertNotIn(payload, content, "XSS payload FOUND (vulnerability still exists)")
        self.assertIn(escaped_payload, content, "Escaped payload NOT found (fix validation)")

    def test_xss_in_region_request(self):
        payload = "<script>alert('XSS')</script>"
        # Send a region that doesn't match 'na' to trigger the error message
        response = self.app.get(f'/valorant/request/1234/5678?region={payload}')

        content = response.get_data(as_text=True)

        # The payload should be escaped now
        escaped_payload = "&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;"

        self.assertNotIn(payload, content, "XSS payload FOUND (vulnerability still exists)")
        self.assertIn(escaped_payload, content, "Escaped payload NOT found (fix validation)")

if __name__ == '__main__':
    unittest.main()
