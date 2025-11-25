import unittest
from unittest.mock import patch, MagicMock
from app.utils.signature_service import NexxitOneshotProvider, SignatureServiceFactory
from app.models import User, Condominium

class TestNexxitOneshotProvider(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_key"
        self.service = NexxitOneshotProvider(self.api_key)
        
    @patch('app.utils.signature_service.requests.post')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=b"pdf_content")
    def test_create_flow_success(self, mock_open, mock_post):
        # Mock user
        user = MagicMock()
        user.cedula = "1234567890"
        user.email = "test@example.com"
        user.first_name = "John"
        user.last_name = "Doe"
        user.cellphone = "0999999999"
        user.city = "Quito"
        user.country = "EC"

        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "flow_123"}
        mock_post.return_value = mock_response

        response = self.service.create_flow("dummy/path.pdf", user, "Test Doc")
        
        self.assertEqual(response['id'], "flow_123")
        mock_post.assert_called_once()
        
    @patch('app.utils.signature_service.requests.get')
    def test_get_flow_details(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "completed", "files": []}
        mock_get.return_value = mock_response
        
        response = self.service.get_flow_details("flow_123")
        self.assertEqual(response['status'], "completed")

    def test_factory_method(self):
        # Test fallback for Punta Blanca
        condo = MagicMock()
        condo.subdomain = "puntablanca"
        condo.signature_provider_config = None
        
        service = SignatureServiceFactory.get_provider(condo)
        self.assertIsNotNone(service)
        self.assertIsInstance(service, NexxitOneshotProvider)
        self.assertEqual(service.api_key, "508f23a8cc4806b35687f696e9ac601c4556a53453d709b2a1a13e3d221d22ad")
        
        # Test no config and other subdomain
        condo.subdomain = "other"
        service = SignatureServiceFactory.get_provider(condo)
        self.assertIsNone(service)
        
        # Test custom config
        condo.subdomain = "other"
        condo.signature_provider_config = {"api_key": "custom_key"}
        service = SignatureServiceFactory.get_provider(condo)
        self.assertIsNotNone(service)
        self.assertEqual(service.api_key, "custom_key")

if __name__ == '__main__':
    unittest.main()
