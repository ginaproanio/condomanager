import unittest
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models import User, Condominium, Payment, Document
from app.services.user_service import UserService
from app.services.payment_service import PaymentService
from app.services.document_service import DocumentService
from flask import current_app
import io

class TestServices(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Setup Data
        self.condo = Condominium(
            name="Test Condo", subdomain="test", status="ACTIVO", environment="production",
            main_street="Main", cross_street="Cross", city="City",
            payment_config={'token': 'fake_token'}
        )
        db.session.add(self.condo)
        db.session.commit()

        self.user = User(
            email="test@test.com", first_name="Test", last_name="User",
            cedula="1234567890", role="USER", status="active",
            condominium_id=self.condo.id, tenant="test"
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_service_update_social(self):
        form_data = {
            'twitter_profile': 'twitter_handle',
            'facebook_profile': 'facebook_handle'
        }
        user = UserService.update_social_profiles(self.user.id, form_data)
        self.assertEqual(user.twitter_profile, 'twitter_handle')
        self.assertEqual(user.facebook_profile, 'facebook_handle')

    def test_payment_service_manual_report(self):
        # Mock file
        file = MagicMock()
        file.filename = 'comprobante.pdf'
        file.mimetype = 'application/pdf'
        
        form_data = {
            'amount': '50.00',
            'description': 'Pago Enero'
        }
        
        with patch('app.services.payment_service.validate_file') as mock_val_file:
            with patch('werkzeug.datastructures.FileStorage.save'): # Mock file save
                payment = PaymentService.report_manual_payment(
                    self.user.id, self.condo.id, form_data, file
                )
                
                self.assertIsNotNone(payment.id)
                self.assertEqual(payment.amount, 50.00)
                self.assertEqual(payment.status, 'PENDING_REVIEW')

    @patch('app.services.payment_service.PayPhoneService')
    def test_payment_service_initiate_payphone(self, MockPayPhone):
        # Mock service instance
        mock_service = MockPayPhone.return_value
        mock_service.prepare_payment.return_value = {
            'paymentId': 12345,
            'payWithCard': 'https://payphone.com/pay'
        }
        
        form_data = {'amount': '100', 'description': 'Alícuota'}
        
        redirect_url = PaymentService.initiate_payphone_payment(self.user, self.condo.id, form_data)
        
        self.assertEqual(redirect_url, 'https://payphone.com/pay')
        
        # Check DB
        payment = Payment.query.filter_by(payphone_transaction_id='12345').first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, 100.0)

    def test_document_service_create(self):
        form_data = {
            'title': 'Acta Asamblea',
            'content': '<p>Contenido</p>',
            'document_type': 'ACTA'
        }
        
        with patch('app.services.document_service.DocumentService.generate_unsigned_pdf'):
            doc = DocumentService.create_document(self.user, form_data, self.condo)
            
            self.assertIsNotNone(doc.id)
            self.assertEqual(doc.title, 'Acta Asamblea')
            self.assertTrue(doc.document_code.startswith('ACTA'))

if __name__ == '__main__':
    unittest.main()

