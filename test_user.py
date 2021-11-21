import os
from unittest import TestCase
from models import db, connect_db, User, Crypto, Inventory
from unittest import TestCase
from flask import session


os.environ['DATABASE_URL'] = "postgres:///eight_bit_banking_db"


from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['TESTING'] = True


class EightBitBankingTestCase(TestCase):
    def test_register_page(self):
        with app.test_client() as client:
            res = client.get('/register')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<form class="usr" method="POST">', html)

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.register(username="testuser",
                                    email="test@test.com",
                                    pwd="testuser")
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id


        db.session.add(self.testuser)
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_accont(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            resp = c.get(f"/account/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)
            
            self.assertIn("testuser", str(resp.data))

    def test_user_deletion(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            resp = c.post(f"/account/{self.testuser_id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            
            user = User.query.filter(User.id==self.testuser_id).all()
            username = User.query.filter(User.username=="testuser").all()
            email = User.query.filter(User.email=="test@test.com").all()
            pwd = User.query.filter(User.password=="testuser").all()
            
            self.assertEqual(len(user), 0)
            self.assertEqual(len(username), 0)
            self.assertEqual(len(email), 0)
            self.assertEqual(len(pwd), 0)

    def setup_cryptos(self):
        BTC = Crypto(crypt_name="BTC", amount=12345, user_id=self.testuser_id)
        XRP = Crypto(crypt_name="XRP", amount=111, user_id=self.testuser_id)
        AVAX = Crypto(crypt_name="AVAX", amount=222, user_id=self.testuser_id)

        db.session.add_all([BTC, XRP, AVAX])
        db.session.commit()

    def test_user_inventory(self):

        self.setup_cryptos()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
                    
            resp = c.get(f"/inventory/{self.testuser_id}", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            
            self.assertIn("BTC", str(resp.data))
            self.assertIn("12345", str(resp.data))
            self.assertIn("XRP", str(resp.data))
            self.assertIn("111", str(resp.data))
            self.assertIn("AVAX", str(resp.data))
            self.assertIn("222", str(resp.data))

    def inventory_crypto_setup(self):
        BTC = Crypto(crypt_name="BTC", amount=12345, user_id=self.testuser_id)
        BTCI = Inventory(user_id=self.testuser_id, crypt_id=1, amount=12345)
        db.session.add_all([BTC, BTCI])
        db.session.commit()

    def test_crypto_deletion(self):

        self.inventory_crypto_setup()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

        co = Inventory.query.filter(Inventory.crypt_id==1).one()

        resp = c.post(f"/inventory/{co.crypt_id}/delete", follow_redirects=True)
        
        self.assertEqual(resp.status_code, 200)

        cryptos = Inventory.query.filter(Inventory.crypt_id==co.crypt_id).all()
        amount = Inventory.query.filter(Inventory.amount==co.amount).all()

        self.assertEqual(len(cryptos), 0)
        self.assertEqual(len(amount), 0)


          



