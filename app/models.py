from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    calendarID = db.Column(db.String(500), unique=True)
    calendarGroupID = db.Column(db.String(500), unique=False)

    def __init__(self, name=None, calendarID=None, calendarGroupID=None):
        self.name = name
        self.calendarID = calendarID
        self.calendarGroupID = calendarGroupID
    
    def __repr__(self):
        return f'<Calendar for : {self.name!r}>'


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))
    
    def __init__(self, username=None):
        self.username = username

    def __repr__(self):
        return f'<User {self.username!r}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
