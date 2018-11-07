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
  appeals = db.relationship("BanAppeal")
  job_listings = db.relationship("JobListing")
  reports = db.relationship("Report")
  bans = db.relationship("Ban")
  data_requests = db.relationship("GDPRRequest")
  roles = db.relationship(
      'Role',
      secondary=roles_users,
      backref=db.backref('users', lazy='dynamic')
  )


class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True, unique=True)
  poster_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  creation_date = db.Column(db.DateTime)
  comments = db.relationship("Comment")
  title = db.Column(db.String(255), nullable=False)
  link = db.Column(db.String(512), nullable=False)
  score = db.Column(db.Integer, nullable=False)
  reports = db.relationship("Report")
  takedown_id = db.Column(db.Integer, db.ForeignKey("dmca_take_down.id"))

  def author(self):
    return User.query.filter_by(id=self.poster_id).all()[0].username

class Comment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  text = db.Column(db.String(2000))
  creation_date = db.Column(db.DateTime)
  poster_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  parent_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
  post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
  reports = db.relationship("Report")
  replies = db.relationship(
      'Comment',
      backref=db.backref('parent', remote_side=[id]),
      lazy='dynamic'
  )


class JobListing(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  poster_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  reports = db.relationship("Report")
  title = db.Column(db.String(255))
  creation_date = db.Column(db.DateTime)


class Ban(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  reports = db.relationship("Report")
  ban_date = db.Column(db.DateTime)
  expiry_date = db.Column(db.DateTime)
  appeal = db.relationship("BanAppeal", uselist=False, backref="ban")
  post = db.Column(db.Boolean())
  comment = db.Column(db.Boolean())
  vote  = db.Column(db.Integer)

class Report(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  comment_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
  post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
  job_id = db.Column(db.Integer, db.ForeignKey("job_listing.id"))
  reporter_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  ban_id = db.Column(db.Integer, db.ForeignKey("ban.id"))
  reason = db.Column(db.String(500))
  creation_date = db.Column(db.DateTime)

class BanAppeal(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  ban_id = db.Column(db.Integer, db.ForeignKey("ban.id"))
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  creation_date = db.Column(db.DateTime)
  appeal_reason = db.Column(db.String(500))

class DMCATakeDown(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  issuer_name = db.Column(db.String(100))
  issuer_reason = db.Column(db.String(5000))
  posts = db.relationship("Post")
  creation_date = db.Column(db.DateTime)
  fulfillment_date = db.Column(db.DateTime)

class GDPRRequest(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  creation_date = db.Column(db.DateTime)
  fulfillment_date = db.Column(db.DateTime)