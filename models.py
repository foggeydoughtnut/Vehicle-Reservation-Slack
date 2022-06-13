from sqlalchemy import Column, Integer, String
from database import Base
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    calendarID = Column(String(500), unique=True)
    calendarGroupID = Column(String(500), unique=False)

    def __init__(self, name=None, calendarID=None):
        self.name = name
        self.calendarID = calendarID
    
    def __repr__(self):
        return f'<Calendar for : {self.name!r} Id : {self.calendarID!r}>'

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(128))
    
    def __init__(self, username=None):
        self.username = username
    def __repr__(self):
        return f'<User {self.username!r}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
