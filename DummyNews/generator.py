import random
from datetime import datetime

from DummyNews.models import User, Role, Post, Comment, JobListing, BanAppeal, Ban, GDPRRequest, DMCATakeDown, Report

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

def get_or_create_users(db, n):
  users = User.query.all()

  if len(users) < n:
    users += RandomUser(db).generate(n - len(users))

  return users

class CommentGenerator(object):

  def __init__(self, db_session):
    self.db = db_session

  def generate(self, n, parent=0, replies=False):
    comments = []
    for _ in range(n):
      c = Comment(text=fake.sentence(nb_words=15), parent_id=parent)
      if replies:
        c.replies = self.generate(10, parent=c.id, replies=False)
      self.db.session.add(c)
      comments.append(c)

    self.db.session.commit()
    return comments


class RandomPost(object):

  def __init__(self, db_session):
    self.db = db_session

  def generate(self, n):
    posts = []
    users = get_or_create_users(self.db, 10)

    for _ in range(n):
      comments = CommentGenerator(db_session=self.db).generate(10, parent=0, replies=True)
      posts.append( Post(
        poster_id=rnd(users).id, title=fake.sentence(nb_words=10),
        link='https://placehold.it/400x70', score=random.randint(32, 256), comments=comments
      ))

      self.db.session.add(posts[len(posts) -1])
    
    self.db.session.commit()

def get_or_create_posts(db, n):
  posts = Post.query.all()

  if len(posts) < n:
    posts += RandomPost(db).generate(n - len(posts))

  return posts

class RandomJobListing(object):

  def __init__(self, db_session):
    self.db = db_session

  def generate(self, n):
    jobs = []
    users = get_or_create_users(self.db, 10)

    for _ in range(n):
      jobs.append(JobListing(poster_id=rnd(users).id, title=fake.sentence(nb_words=10)))
      self.db.session.add(jobs[len(jobs) -1])
    
    self.db.session.commit()

def get_or_create_jobs(db, n):
  jobs = JobListing.query.all()

  if len(jobs) < n:
    jobs += RandomJobListing(db).generate(n - len(jobs))

  return jobs

def get_or_create_comments(db, n):
  comments = Comment.query.all()

  if len(comments) < n:
    comments += RandomJobListing(db).generate(n - len(comments))

  return comments

class RandomBan(object):

  def __init__(self, db_session):
    self.db = db_session

  def generate(self, n):

    users = get_or_create_users(self.db, 10)
    bans = []

    for _ in range(n):
      bans.append(Ban(
        user_id = rnd(users).id,
        ban_date = datetime.now(), expiry_date = datetime.now(),
        post = rnd([True, False]),
        comment = rnd([True, False]), vote = rnd([True, False])
      ))

      self.db.session.add(bans[len(bans)-1])

    self.db.session.commit()



class RandomBanAppeal(object):
  def __init__(self, db_session):
    self.db = db_session

  def get_or_create_bans(self, n):
    bans = Ban.query.all()

    if len(bans) < n:
      bans += RandomUser(self.db).generate(n - len(bans))

    return bans

  def generate(self, n):

    appeals = []

    bans = self.get_or_create_bans(n)

    for _ in range(n):
      ban = rnd(bans)
      appeals.append(BanAppeal(
        ban_id=ban.id, user_id = ban.user_id,
        appeal_reason = fake.sentence(nb_words=20),
        creation_date = datetime.now()
      ))
      self.db.session.add(appeals[len(appeals) - 1])


    self.db.session.commit()
    pass

class RandomGDPR(object):

  def __init__(self, db_session):
    self.db = db_session

  def generate(self, n):

    users = get_or_create_users(self.db, n)
    gdpr = []

    for _ in range(n):
      gdpr.append(GDPRRequest(
        user_id = rnd(users).id,
        creation_date = datetime.now(),
        fulfillment_date = datetime.now()
      ))

      self.db.session.add(gdpr[len(gdpr) -1])

    self.db.session.commit()
    return gdpr

class RandomDMCA(object):

  def __init__(self, db_session):
    self.db = db_session

  def generate(self, n):

    dmca = []

    for _ in range(n):
      dmca.append(DMCATakeDown(
        issuer_name = fake.sentence(nb_words=3),
        issuer_reason = fake.sentence(nb_words=30),
        creation_date = datetime.now(),
        fulfillment_date = datetime.now()
      ))

      self.db.session.add(dmca[len(dmca) -1])

    self.db.session.commit()

    return dmca

class RandomReport(object):

  def __init__(self, db_session):
    self.db = db_session

  def generate(self, n):

    reports = []

    for _ in range(n):
      for r in [self.report_post(), self.report_job(), self.report_comment()]:
        self.db.session.add(r)
        reports.append(r)


    self.db.session.commit()
    return reports

  def report_post(self):
    return Report(
      reason=fake.sentence(nb_words=20),
      reporter_id=rnd(get_or_create_users(self.db, 10)).id,
      post_id=rnd(get_or_create_posts(self.db, 10)).id,
      creation_date=datetime.now()
    )

  def report_job(self):
    return Report(
      reason=fake.sentence(nb_words=20),
      reporter_id=rnd(get_or_create_users(self.db, 10)).id,
      job_id=rnd(get_or_create_jobs(self.db, 10)).id,
      creation_date=datetime.now()
    )

  def report_comment(self):
    return Report(
      reason=fake.sentence(nb_words=20),
      reporter_id=rnd(get_or_create_users(self.db, 10)).id,
      comment_id=rnd(get_or_create_comments(self.db, 10)).id,
      creation_date=datetime.now()
    )
