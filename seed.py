from app import db
from models import User, Crypto, Inventory

db.drop_all()
db.create_all()

cryp = Crypto(crypt_name="XRP")
db.session.add(cryp)
db.session.commit()

#  plsng = PlaylistSong (playlist_id=1, song_id=1)
#  db.session.add(plsng)
#  db.session.commit()

