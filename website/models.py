from . import db #imports database 'db' from the current directory defined in __init__.py

from flask_login import UserMixin #allows us to make a user object based on the login
#from sqlalchemy.sql import func

from datetime import datetime
from pytz import timezone
from .constants import MY_TIMEZONE


def get_now():
    return datetime.strptime(((datetime.now()).astimezone(timezone(MY_TIMEZONE))).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=False), default=get_now())
    #ensures a valid user id must be passed upon creation of this note object, 
    #allows a one to many relationship (one user, with multiple notes)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #a foreign key references the id of another database table (same name as class)


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True) #primary key means it's the id
    email = db.Column(db.String(150), unique=True)
    is_admin = db.Column(db.Boolean)
    password = db.Column(db.String(150))
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    datetime_joined = db.Column(db.DateTime(timezone=False), default=get_now())
    
    role = db.Column(db.String(150), default="General")

    phoneNumber = db.Column(db.String(50), default="Not Specified") 
    streetAddress = db.Column(db.String(150))
    city = db.Column(db.String(100))
    state = db.Column(db.String(5))
    zipcode = db.Column(db.String(10))

    notes = db.relationship('Note') #stores all notes associated with each user, (same name as class with exactly same casing)
    activeShift_id = db.Column(db.Integer, default=0)
    shiftsWorked = db.relationship('Shift') #stores all archived job
    # EVENTUALLY MAKE THE ID OF THE ACTIVE_JOBS CLASS

    roles_held = db.relationship('RoleHolders') #multiple


    #TODO - one user can have multiple roles

    #roles_ids = db.Column(db.Integer, db.ForeignKey('role.id'))
    #roles = db.relationship('Role', foreign_keys=[roles_ids])

#still needs more work, split into ArchivedJobs and ActiveJobs, and active jobs can have multiple users associated with it
class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True) #id
    datetime_clockin = db.Column(db.DateTime(timezone=False))

    datetime_clockout = db.Column(db.DateTime(timezone=False))
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)

    total_hours = db.Column(db.Float, default=0.0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    client_id = db.Column(db.Integer, db.ForeignKey('client.id')) 
    note = db.Column(db.String(10000), default="")

    role_id = db.Column(db.Integer, db.ForeignKey('role.id')) 
    role_name_for_shift = db.Column(db.String(150))
    payrate_for_shift = db.Column(db.Float, default=0.0)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True) #id
    
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    company = db.Column(db.String(150))
    
    email = db.Column(db.String(150), unique=True)

    phoneNumber = db.Column(db.String(50))
    streetAddress = db.Column(db.String(150))
    city = db.Column(db.String(100))
    state = db.Column(db.String(5))
    zipcode = db.Column(db.String(10))

    shiftsReceived = db.relationship('Shift')
    datetime_added = db.Column(db.DateTime(timezone=False), default=get_now())

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True) #id
    role_name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(1000), default="")

    payrate = db.Column(db.Float, default=0.0)

    def payrate_str(self):
        return f"${format(self.payrate, '.2f')} / hour"

    role_holders = db.relationship('RoleHolders') #multiple
    shifts_with_role = db.relationship('Shift')

    datetime_added = db.Column(db.DateTime(timezone=False), default=get_now())

class RoleHolders(db.Model):
    # id = db.Column(db.Integer, primary_key=True) #id
    #acts as a linkage between users and roles
    #one user can have multiple roles, and one role can have multiple users
    holder_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True) #one
    held_role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key = True) #one