import random

from DummyNews.models import User, Role, Post, Comment, JobListing

from faker import Factory
from faker.providers import lorem, internet

fake = Factory.create()
fake.add_provider(lorem)
fake.add_provider(internet)

rnd = lambda a: a[random.randint(0, len(a) -1)]

class RandomUser(object):

  Roles = ["Admin", "Moderator", "User"]

  def __init__(self, db_session):
    self.db = db_session


  def generate(self, n):
    users = []

    roles = self._roles(RandomUser.Roles)
    rnd = lambda a: a[random.randint(0, len(a) -1)]

    for _ in range(n):
      users.append(User(email=fake.email(), username=fake.user_name(), roles = [rnd(list(roles.values()))], active=1, password='12345'))
      self.db.session.add(users[len(users)-1])

    self.db.session.commit()

    return users

  def _roles(self, roles):
    roles = {role: Role(name=role, description='Lorem ipsum sit amet') for role in roles}
    for r in roles.values(): self.db.session.add(r)

    self.db.session.commit()
    return roles

class CommentGenerator(object):

  def __init__(self, db_session):
    self.db = db_session

  def generate(self, n, parent=0, replies=False):
    comments = []
    for _ in range(n):
      c = Comment(text=fake.sentence(nb_words=250), parent_id=parent)
      if replies:
        c.replies = self.generate(10, parent=c.id, replies=False)
      self.db.session.add(c)
      comments.append(c)

    self.db.session.commit()
    return comments


class RandomPost(object):

  def __init__(self, db_session):
    self.db = db_session

  def get_or_create_users(self, n):
    users = User.query.all()

    if len(users) < n:
      users += RandomUser(self.db).generate(n - len(users))

    return users

  def generate(self, n):
    posts = []
    users = self.get_or_create_users(10)

    for _ in range(n):
      comments = CommentGenerator(db_session=self.db).generate(10, parent=0, replies=True)
      posts.append( Post(
        poster_id=rnd(users).id, title=fake.sentence(nb_words=10),
        link='https://placehold.it/400x70', score=random.randint(32, 256), comments=comments
      ))

      self.db.session.add(posts[len(posts) -1])
    
    self.db.session.commit()

class RandomJobListing(object):

  def __init__(self, db_session):
    self.db = db_session

  def get_or_create_users(self, n):
    users = User.query.all()

    if len(users) < n:
      users += RandomUser(self.db).generate(n - len(users))

    return users

  def generate(self, n):
    jobs = []
    users = self.get_or_create_users(10)

    for _ in range(n):
      jobs.append(JobListing(poster_id=rnd(users).id, title=fake.sentence(nb_words=10)))
      self.db.session.add(jobs[len(jobs) -1])
    
    self.db.session.commit()