from flask import Flask, render_template, request, jsonify

from DummyNews.models import *
from DummyNews.generator import RandomUser, RandomPost, RandomJobListing

def create_app(environment=None):

  app = Flask(__name__)
  app.config.from_object('config')
  app.config['ENVIRONMENT'] = environment

  db.init_app(app)

  @app.route('/')
  @app.route('/index')
  def index():
    return render_template('index.html', posts=Post.query.all())

  @app.route('/post/<int:id>', methods=['GET'])
  def view_post(id):
    r = Post.query.filter_by(id=id).all()
    if len(r) < 1:
      return render_template('404.html')

    return render_template('post.html', post=r[0])

  @app.before_first_request
  def before_first_request():
    db.drop_all()
    db.create_all()

    RandomUser(db_session=db).generate(20)
    RandomPost(db_session=db).generate(20)
    RandomJobListing(db_session=db).generate(100)

    db.session.commit()
    pass

  return app