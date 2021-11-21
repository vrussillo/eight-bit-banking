import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Inventory, Crypto


os.environ['DATABASE_URL'] = "postgres:///eight_bit_banking_db"

from app import app
db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test for Register form for User Model"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.register("usertest1", "email1@email.com", "password")
        uid1 = 100
        u1.id = uid1

        u2 = User.register("usertest2", "email2@email.com", "password")
        uid2 = 200
        u2.id = uid2

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_user_model(self):

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(len(u.cryptos), 0)
        self.assertEqual(len(u.amount), 0)


    def test_valid_register(self):
        u_test = User.register("testtest", "testtest@test.com", "password")
        uid = 99999
        u_test.id = uid
        db.session.add(u_test)
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertEqual(u_test.username, "testtest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_register(self):
        invalid = User.register(None, "test@test.com", "password")
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.add(invalid)
            db.session.commit()

    def test_invalid_email_register(self):
        invalid = User.register("testtest", None, "password")
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.add(invalid)
            db.session.commit()
    
    def test_invalid_password_register(self):
        with self.assertRaises(ValueError) as context:
            User.register("testtest", "email@email.com", "")
        
        with self.assertRaises(ValueError) as context:
            User.register("testtest", "email@email.com", None)


    
    def test_valid_authentication(self):
        """User authentification test"""
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("invalidusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "invalidpassword"))


class CryptoModelTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u3 = User.register("usertest3", "email1@email.com", "password")
        uid3 = 300
        u3.id = uid3

        db.session.add(u3)
        db.session.commit()

        u3 = User.query.get(uid3)

        self.u3 = u3
        self.uid3 = uid3

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_crypto_model(self):
        """allocate Cypto to User"""
        
        c = Crypto(
            crypt_name="BTC",
            amount="1234.0",
            user_id=self.uid3
        )


        db.session.add(c)
        db.session.commit()

        # User should have 1 crypto
        self.assertEqual(len(self.u3.cryptos), 1)
        self.assertEqual(self.u3.cryptos[0].crypt_name, "BTC")
        self.assertEqual(self.u3.cryptos[0].amount, 1234.0)
