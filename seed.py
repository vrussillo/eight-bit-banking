from app import db
from models import User, Crypto, Inventory

# db.drop_all()
db.create_all()


user = User(username="bigpoppa", email="vrussillo@gmail.com", password="farts69")
db.session.add(user)
db.session.commit()

cryp = Crypto(user_id=1, crypt_name="XRP", amount=345.40)

db.session.add(cryp)
db.session.commit()

inv = Inventory(user_id=1, crypt_id=1, amount=345.40)

db.session.add(inv)
db.session.commit()





