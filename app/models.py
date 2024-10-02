from typing import Optional
import sqlalchemy as sa
from datetime import datetime, timezone
from hashlib import md5
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
 
followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', Integer, ForeignKey('users.id'),
           primary_key=True),
    sa.Column('followed_id', Integer, ForeignKey('users.id'),
           primary_key=True)
) 
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True)
    email = Column(String(120), index=True, unique=True)
    password_hash = Column(String(256))
    about_me = Column(String(140))
    posts = relationship('Post', backref='user', lazy='dynamic')
    
    followed = relationship(
        "User", secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )


    following = relationship(
        "User", secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers'
    )

    followed = relationship(
        "User", secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(user.id==user.id)
        return db.session.scalar(query)is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)
        

    def following_count(self):
        query= sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
          raise ValidationError('Please use a different username.')
      
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )
        
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    body = Column(String(140))
    timestamp = Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)

    author = relationship("User", back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)