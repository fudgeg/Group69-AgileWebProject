from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

#many to many association table for friendships
friend_association = db.Table('friendships',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_picture = db.Column(db.String(100), default='user.png')

 # Symmetric friend relationship logic update (saves both directions)
    # Many-to-many relationship for friends
    # This allows us to access friends from both sides of the relationship
    # user.friends and user.friend_of
    friends = db.relationship(
        'User',
        secondary=friend_association,
        primaryjoin=id == friend_association.c.user_id,
        secondaryjoin=id == friend_association.c.friend_id,
        backref='friend_of'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
    
class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default="pending")
    seen = db.Column(db.Boolean, default=False)  # New field

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')


class MediaEntry(db.Model):
    __tablename__ = 'media_entry'
    id = db.Column(db.Integer, primary_key=True)
    media_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    # Optional Comments Field
    comments = db.Column(db.Text, nullable=True)
    consumed_date = db.Column(db.Date, nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)
    # Foreign key to link media entry to the User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Relationship to access User from MediaEntry (entry.user)
    user = db.relationship('User', backref='media_entries')

    __mapper_args__ = {
        'polymorphic_identity': 'media_entry',
        'polymorphic_on': media_type
    }

    def __repr__(self):
        return f"<{self.media_type}: {self.title}>"

class Movie(MediaEntry):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, db.ForeignKey('media_entry.id'), primary_key=True)
    genre = db.Column(db.String(50), nullable=True)
    watched_date = db.Column(db.Date, nullable=True)
    # Relationship to access MediaEntry from Movie (movie.media_entry)
   
    __mapper_args__ = {'polymorphic_identity': 'movie'}

    def __repr__(self):
        return f"<Movie {self.title}, Genre: {self.genre}>"
    
class TVShow(MediaEntry):
    __tablename__ = 'tv_shows'
    id = db.Column(db.Integer, db.ForeignKey('media_entry.id'), primary_key=True)
    genre= db.Column(db.String(50), nullable=True)
    watched_date = db.Column(db.Date, nullable=True)
    __mapper_args__ = {'polymorphic_identity': 'tv_show'}
    def __repr__(self):
        return f"<TVShow {self.title}, Genre: {self.genre}>"
class Music(MediaEntry):
    __tablename__ = 'music'
    id = db.Column(db.Integer, db.ForeignKey('media_entry.id'), primary_key=True)
    genre = db.Column(db.String(50), nullable=True)
    artist = db.Column(db.String(100), nullable=True)
    listened_date = db.Column(db.Date, nullable=True)
    __mapper_args__ = {'polymorphic_identity': 'music'}
    def __repr__(self):
        return f"<Music {self.title}, Artist: {self.artist}>"

class Book(MediaEntry):
    __tablename__ = 'books'
    id = db.Column(db.Integer, db.ForeignKey('media_entry.id'), primary_key=True)
    genre = db.Column(db.String(50), nullable=True)
    author = db.Column(db.String(100), nullable=True)
    date_started = db.Column(db.Date, nullable=True)
    date_finished = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=True) # e.g., "reading", "completed", "on hold"
    # Relationship to access MediaEntry from Book (book.media_entry)
    __mapper_args__ = {'polymorphic_identity': 'book'}
    def __repr__(self):
        return f"<Book {self.title}, Author: {self.author}>"

