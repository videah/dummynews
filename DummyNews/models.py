from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

roles_users = db.Table(
  'roles_users',
  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
  db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):

  id = db.Column(db.Integer, primary_key=True, unique=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))

  def __str__(self):
      return self.name

  def __hash__(self):
      return hash(self.name)


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True, unique=True)
  username = db.Column(db.String(32), unique=True, nullable=False)
  email = db.Column(db.String(255), unique=True, nullable=False)
  password = db.Column(db.String(255), nullable=False)
  active = db.Column(db.Boolean())
  created_at = db.Column(db.DateTime())
  posts = db.relationship("Post")
  comments = db.relationship("Comment")
  job_listings = db.relationship("JobListing")
  roles = db.relationship(
      'Role',
      secondary=roles_users,
      backref=db.backref('users', lazy='dynamic')
  )


class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True, unique=True)
  poster_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  comments = db.relationship("Comment")
  title = db.Column(db.String(255), nullable=False)
  link = db.Column(db.String(512), nullable=False)
  score = db.Column(db.Integer, nullable=False)

  def author(self):
    return User.query.filter_by(id=self.poster_id).all()[0].username

class Comment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  text = db.Column(db.String(2000))
  poster_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  parent_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
  post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
  replies = db.relationship(
      'Comment',
      backref=db.backref('parent', remote_side=[id]),
      lazy='dynamic'
  )


class JobListing(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  poster_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  title = db.Column(db.String(255))


class Ban(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  post = db.Column(db.Boolean())
  comment = db.Column(db.Boolean())
  vote  = db.Column(db.Integer)
