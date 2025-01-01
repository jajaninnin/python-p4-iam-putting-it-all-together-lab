from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.Integer)

    #relationship
    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')

    #serialize rules
    serialize_rules = ('-recipes',)

    @property
    def password_hash(self):
        raise AttributeError('No direct access of password hash')
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    #relationship
    user = db.relationship('User', back_populates='recipes')
    
    #serialize rules
    # serialize_rules = ('-users',)

    @validates('instructions')
    def validate_instructions(self, key, value):
        if len(value) < 50:
            raise ValueError('Listing must have a nearby airport and min 1 char')
        return value
    