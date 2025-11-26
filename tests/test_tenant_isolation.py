import unittest
from app import create_app, db
from app.models import User, Condominium
from flask import g

class TestTenantIsolation(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create 2 Tenants
        self.tenant1 = Condominium(
            name="Tenant 1", subdomain="t1", status="ACTIVO", environment="production",
            main_street="Main St", cross_street="Cross St", city="Quito"
        )
        self.tenant2 = Condominium(
            name="Tenant 2", subdomain="t2", status="ACTIVO", environment="production",
            main_street="Main St", cross_street="Cross St", city="Quito"
        )
        db.session.add_all([self.tenant1, self.tenant2])
        db.session.commit()

        # Create Users
        # Note: We must set condominium_id manually here because we are not in a request context 
        # and the listener depends on g.condominium which is unset.
        self.user1 = User(
            email="u1@t1.com", 
            first_name="U1", last_name="T1", 
            cedula="111", 
            condominium_id=self.tenant1.id,
            tenant="t1"
        )
        self.user2 = User(
            email="u2@t2.com", 
            first_name="U2", last_name="T2", 
            cedula="222", 
            condominium_id=self.tenant2.id,
            tenant="t2"
        )
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_query_without_tenant_context(self):
        """Without g.condominium, should return all or behave as standard"""
        print(f"DEBUG: User.query type: {type(User.query)}")
        # g.condominium is None by default
        users = User.query.all()
        self.assertEqual(len(users), 2, "Should see all users when no tenant is active")

    def test_query_with_tenant_context(self):
        """With g.condominium, should ONLY return users of that tenant"""
        
        # Simulate Request Context / Middleware
        g.condominium = self.tenant1
        
        users = User.query.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, "u1@t1.com")
        
        # Switch Tenant
        g.condominium = self.tenant2
        users = User.query.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, "u2@t2.com")

    def test_get_by_id_protection(self):
        """User.query.get(id) should return None if ID belongs to another tenant"""
        g.condominium = self.tenant1
        
        # Try to get User 2 (who belongs to Tenant 2)
        user = User.query.get(self.user2.id)
        self.assertIsNone(user, "Should not be able to fetch User 2 from Tenant 1 context")
        
        # Try to get User 1
        user = User.query.get(self.user1.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user1.id)

    def test_auto_injection_listener(self):
        """New objects should auto-inherit tenant ID"""
        g.condominium = self.tenant1
        
        new_user = User(
            email="auto@t1.com", 
            first_name="Auto", last_name="Inject", 
            cedula="333"
            # No condominium_id provided
        )
        db.session.add(new_user)
        db.session.commit()
        
        self.assertEqual(new_user.condominium_id, self.tenant1.id)

if __name__ == '__main__':
    unittest.main()

