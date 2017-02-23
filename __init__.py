from flask import Flask, request, render_template, redirect, url_for, abort
from google.appengine.ext import ndb
from google.appengine.ext.db import BadRequestError
from models.auth import User
from models.blog import BlogPost
from utils.security import Security
import mistune


app = Flask(__name__, template_folder="views",
            static_folder='bld', static_url_path='/static')
app.debug = True
sec = Security(app, 'shh')
md = mistune.Markdown()
app.jinja_env.filters['md'] = md


def get_user(token=None, username=None):
  username = username or token.get('usr') if token else None
  user = User.query(User.username == username).get()
  return user


def get_post(post_id):
  try:
    return BlogPost.get_by_id(post_id)
  except BadRequestError as ex:
    return None


@app.route("/")
@app.route("/<int:offset>")
def root(offset=0):
  user = None
  next = offset + 10
  prev = offset - 10 if offset >= 10 else 0
  if sec.token.get('usr'):
    user = User()
    user.fill(username=sec.token.get('usr'))
  try:
    posts = BlogPost.gql('ORDER BY created DESC LIMIT 10 OFFSET %s' % offset)
    return render_template('index.html', page=None, user=user,
                            posts=posts, next=next, prev=prev)
  except Exception as ex:
    print(ex)
    abort(404)
  # return render_template('index.html', page=None, user=user)


@app.route("/view/<int:post_id>")
def view(post_id):
  user = None
  post = get_post(post_id)
  if sec.token.get('usr'):
    user = User()
    user.fill(username=sec.token.get('usr'))
  if post:
    return render_template('view.html', page=None, user=user,
                            post=post)
  else:
    abort(404)


@app.route("/edit/", methods=['GET', 'POST'])
@app.route("/edit/<int:post_id>", methods=['GET', 'POST'])
def edit(post_id=None):
  user = None
  post = get_post(post_id)
  if sec.token.get('usr'):
    user = User()
    user.fill(username=sec.token.get('usr'))

  if request.method == 'POST':
    if request.form.get('cancel'):
      return redirect(url_for('root'))
    post = post or BlogPost()
    post.fill(**request.form.to_dict())
    if not post.empty('subject', 'content'):
      try:
        post.put()
        return redirect(url_for('edit', post_id=post.key.id()))
      except Exception as ex:
        print('post crud error', ex)
        pass
      # print('***************', post.key.urlsafe())
  # print(post)
  return render_template('edit.html', page=None, user=user, post=post)


@app.route("/signup/", methods=['GET', 'POST'])
@sec.allow(lambda t: not t.get('usr'), lambda: redirect(url_for('root')))
def signup():
  user = None
  pass_verified = None
  if request.method == 'POST':
    if request.form.get('cancel'):
      return redirect(url_for('root'))
    try:
      user = User()
      user.fill(**request.form.to_dict())
      pass_verified = request.form.get('verify') == request.form.get('password')
      if user.valid() and user.unique and pass_verified:
        user.put()
        sec.token = {'usr': user.username}
        return redirect(url_for('root'))
    except Exception as ex:
      print('bad user')
      print(ex)
  return render_template('signup.html',
                          page=None, user=user,
                          form_action="/signup/", pass_verified=pass_verified)


@app.route("/signin/", methods=['GET', 'POST'])
@sec.allow(lambda t: not t.get('usr'), lambda: redirect(url_for('root')))
def signin():
  user = None
  user_verified = False
  pass_verified = False
  if request.method == 'POST':
    if request.form.get('cancel'):
      return redirect(url_for('root'))
    try:
      user = User.query(User.username == request.form.get('username', '')).get()
    except Exception as ex:
      pass
    user_verified = True if user else False
    if (user and user.password and
      User.password.verify(request.form.get('password'), user.password)):
      sec.token = {'usr': user.username}
      pass_verified = True
      return redirect(url_for('root'))
    else:
      user = User()
      user.fill(username=request.form.get('username'))
  return render_template('signin.html',
                          page=None, user=user,
                          form_action="/signin/", user_verified=user_verified,
                          pass_verified=pass_verified)


@app.route("/signout/", methods=['GET', 'POST'])
@sec.allow(lambda t: t.get('usr'), lambda: redirect(url_for('signin')))
def signout():
  if request.method == 'POST':
    if request.form.get('cancel'):
      return redirect(url_for('root'))
    sec.token = {}
    return redirect(url_for('root'))
  return render_template('signout.html',
                          page=None, user=None, form_action="/signout/")


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
