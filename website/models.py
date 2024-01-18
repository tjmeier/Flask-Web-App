from . import db #imports database 'db' from the current directory defined in __init__.py

from flask_login import UserMixin #allows us to make a user object based on the login
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    #ensures a valid user id must be passed upon creation of this note object, 
    #allows a one to many relationship (one user, with multiple notes)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #a foreign key references the id of another database table (same name as class)


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    is_admin = db.Column(db.Boolean)
    password = db.Column(db.String(150))
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    #date_joined = db.Column(db.DateTime(timezone=True), default=func.now())
    notes = db.relationship('Note') #stores all notes associated with each user, (same name as class with exactly same casing)