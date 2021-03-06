import datetime
import uuid

import jwt
from flask import current_app
from project import db
from project.error_handlers import BlacklistTokenError
from sqlalchemy import Enum
from project.models.blacklist_token import BlacklistToken
import enum

#-------------------------------------------------------------------------------
# Model
#-------------------------------------------------------------------------------

roles = ('ON_BOARDING', 'MEMBER', 'ADMIN')

class Role(enum.Enum):
    ON_BOARDING = 1
    MEMBER = 2
    ADMIN = 3


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(128), unique=True)
    google_id = db.Column(db.String(128), unique=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    events = db.relationship('Event', backref='user')
    role = db.Column(Enum(Role))
    img_url = db.Column(db.String(2048), unique=True)
    cred = db.relationship('Credential',
                           backref='user',
                           cascade="all, delete-orphan",
                           uselist=False)

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """

        try:
            payload = jwt.decode(auth_token,
                                 current_app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                raise BlacklistTokenError
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError

    def encode_auth_token(self, user_id):
        """
        Encodes a auth token for user
        :params user id
        :return token|bytes

        :token-contents
            exp: expiration date of the token
            iat: the time the token is generated
            sub: the subject of the token (the user whom it identifies)
        """
        try:
            payload = {
                'exp':
                datetime.datetime.utcnow() +
                datetime.timedelta(days=0, seconds=3600),
                'iat':
                datetime.datetime.utcnow(),
                'sub':
                user_id
            }
            return jwt.encode(payload, current_app.config.get('SECRET_KEY'))
        except Exception as e:
            return e


#-------------------------------------------------------------------------------
# Database Functions
#-------------------------------------------------------------------------------


def add_user(name='kenny', email='test@email.com',
             role=Role.ON_BOARDING, **kwargs) -> User:
    """
    Creates a User, adds the created user and returns the created User.
    :param name: (str) the name of the user
    :param email: (str) the unique email of the user
    :return: a User
    """
    user = User(public_id=uuid.uuid4(), name=name, email=email, role=role)
    db.session.add(user)
    return user


def update_user(user, params):
    for key, value in params.items():
        if value is not None:
            setattr(user, key, value)
    db.session.commit()
    return user

def promote_to_member(user):
    user.role = Role.MEMBER
    db.session.commit()
    return user
