from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from backend import db


class UserRoleEnum(Enum):
    USER = 'user'
    ADMIN = 'admin'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), unique=False, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    first_name = db.Column(db.String(150), unique=False, nullable=False)
    last_name = db.Column(db.String(150), unique=False, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}'')"
    
    def serialize(self):
        return {
            'email': self.email,
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }


class Subscriber(db.Model):
    __tablename__ = 'subscribers'

    id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscribed_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    subscriber = db.relationship('User', foreign_keys=[subscriber_id], backref='subscriptions')
    subscribed_to = db.relationship('User', foreign_keys=[subscribed_to_id], backref='subscribers')

    def __repr__(self):
        return f'<Subscriber {self.subscriber_id} subscribed to {self.subscribed_to_id}>'
    
    def serialize(self):
        return {
            'subscriber': self.subscriber,
            'subscribed_to': self.subscribed_to
        }
