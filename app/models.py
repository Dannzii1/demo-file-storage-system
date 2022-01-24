from datetime import datetime

from app import app
from flask_login._compat import unicode
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.orm import relationship
from sqlalchemy import *
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from . import db


class Users(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email_address = Column(String(255), unique=True)
    username = Column(String(80), unique=True, nullable=False)
    __password = Column('password', String(255), nullable=False)
    last_reset_token = Column(String(255))
    token_used = Column(Boolean(), default=False)
    creation_date = Column(DateTime, default=datetime.now)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return '<User %r>' % self.username

    @hybrid_property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        self.__password = password

    def generate_token(self, expires_sec=1800):
        new_token = Serializer(app.config['SECRET_KEY'], expires_sec)
        return new_token.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def validate_token(token):
        check_token = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = check_token.loads(token)['id']
            user = Users.query.get(user_id)
        except:
            app.logger.warn('Token provided is invalid')
            return None
        return user if user and not user.token_used else None


class Documents(db.Model):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    relative_location = Column(String(255), nullable=False)
    creation_date = Column(DateTime, default=datetime.now)

    def __init__(self, user_id, file_name, relative_location):
        self.user_id = user_id
        self.file_name = file_name
        self.relative_location = relative_location

    @staticmethod
    def get_institution_files(user_id, page=1):
        return Documents.query.filter_by(user_id=user_id) \
            .order_by(Documents.creation_date.desc()).paginate(page=page, per_page=5, error_out=False)


