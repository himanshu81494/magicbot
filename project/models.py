# project/models.py


import datetime

from project import db, bcrypt
import datetime

import hashlib
class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    user_token = db.Column(db.String)

    name = db.Column(db.String)
    mobileno = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    contacts = db.Column(db.String)
    gcmid  = db.Column(db.String)
    gcmregid = db.Column(db.String)
    gcmapikey = db.Column(db.String)

    threat = db.Column(db.Boolean, default=False)
    precaution = db.Column(db.String, default ='')


    def __init__(self, email, password, confirmed,
                 admin=False, confirmed_on=None, user_token='', name=''):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.user_token = user_token
        self.name = name


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<email {}'.format(self.email)






class fbUsers(db.Model):

    __tablename__ = "fbusers"

    id = db.Column(db.Integer, primary_key=True)
    fbid = db.Column(db.Integer)
    first_name = db.Column(db.String, default='')
    last_name = db.Column(db.String, default='')
    gender = db.Column(db.String, default='')
    locale = db.Column(db.String, default='')
    profile_pic = db.Column(db.String, default='')
    timezone = db.Column(db.String, default='')
    state = db.Column(db.String, default='')
    # updated_on = db.Column(db.DateTime, server_default=db.func.now())
    

    def __init__(self,fbid, first_name='', last_name='', gender='', locale='', profile_pic='', timezone='', state=''):
        self.fbid = fbid
        self.first_name =  first_name
        self.last_name = last_name
        self.profile_pic = profile_pic
        self.timezone = timezone
        self.locale = locale
        self.state = state


    def get_id(self):
        return self.id

