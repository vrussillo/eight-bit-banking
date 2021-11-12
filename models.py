from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import validates

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """Model for Site user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    inventory = db.relationship("Inventory", backref="user", cascade="all, delete-orphan")
    
    cryptos = db.relationship('Crypto', cascade="all, delete-orphan")
    amount = db.relationship('Crypto', cascade="all, delete-orphan", overlaps="cryptos")

    # start_register
    @classmethod
    def register(cls, username, email, pwd):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, email=email, password=hashed_utf8)
    # end_register

    # start_authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False
        # end_authenticate 


class Inventory (db.Model):

    """Inventory Model for Crypto Insertion"""

    __tablename__ = 'inventory'

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='CASCADE'), primary_key=True)
    crypt_id = db.Column(db.Integer, db.ForeignKey("cryptos.id", ondelete='CASCADE'), primary_key=True)
    amount = db.Column(db.Float, nullable=False)

class Crypto (db.Model):

    """Model for Crypto"""

    __tablename__ = 'cryptos'

    id = db.Column(db.Integer, primary_key=True)
    crypt_name = db.Column(db.Text, nullable=False)
    crypto = db.relationship("Inventory", backref="crypto", cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user = db.relationship('User')

    """ensure that crpto type/name is all uppercase"""
    @validates('id', 'crypt_name')
    def convert_upper(self, key, value):
        return value.upper()





