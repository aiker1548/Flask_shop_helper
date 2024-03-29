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


# class Subscriber(db.Model):
#     __tablename__ = 'subscribers'

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     user = db.relationship('User', backref=db.backref('subscribers', lazy=True))

#     def __repr__(self):
#         return '<Subscriber %r>' % self.email