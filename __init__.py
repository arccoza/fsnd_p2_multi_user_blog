from flask import Flask, request, render_template, redirect, url_for, abort
from google.appengine.ext import ndb
from google.appengine.ext.db import BadRequestError
from models.auth import User
from models.blog import BlogPost
from utils.security import Security
from functools import wraps
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


def post_q(query, out_kw):
  def post_q_deco(fn):
    @wraps(fn)
    def post_q_handler(**kwargs):
      print(query % kwargs)
      return fn(**{out_kw: BlogPost.gql(query % kwargs)})
    return post_q_handler
  return post_q_deco


@app.route("/", defaults={'offset': 0})
@app.route("/<int:offset>")
@BlogPost.q('ORDER BY created DESC LIMIT 10 OFFSET %(offset)s', 'posts')
@User.is_available()
def root(offset=0, posts=None, user=None):
  user = user or None
  posts = posts or None
  next = offset + 10
  prev = offset - 10 if offset >= 10 else 0
  return render_template('index.html', page=None, user=user,
                            posts=posts, next=next, prev=prev)


@app.route("/view/<string:post_id>")
@BlogPost.q('WHERE uid = \'%(post_id)s\'', 'post')
@User.is_available()
def view(post_id=None, post=None, user=None):
  user = user or None
  post = post.get() if post else None
  if post:
    return render_template('view.html', page=None, user=user,
                            post=post)
  else:
    abort(404)


@app.route("/edit/", defaults={'post_id': ''}, methods=['GET', 'POST'])
@app.route("/edit/<string:post_id>", methods=['GET', 'POST'])
@BlogPost.q('WHERE uid = \'%(post_id)s\'', 'post')
@User.is_owner('post', lambda: abort(403))
def edit(post_id=None, post=None, user=None):
  user = user or None
  print('post query:', post)
  post = post.get() if post else None
  print('post get:', post)
  if request.method == 'POST':
    if request.form.get('cancel'):
      return redirect(url_for('root'))
    post = post or BlogPost(parent=user.key)
    post.fill(**request.form.to_dict())
    if not post.empty('subject', 'content'):
      try:
        post.put()
        print('post save:', post.uid)
        return redirect(url_for('edit', post_id=post.uid))
      except Exception as ex:
        print('post crud error', ex)
        pass
  return render_template('edit.html', page=None, user=user, post=post)


@app.route("/delete/<string:post_id>", methods=['GET', 'POST'])
# @BlogPost.q('WHERE __key__ = KEY(\'BlogPost\', %(post_id)s)', 'post')
@BlogPost.q('WHERE uid = \'%(post_id)s\'', 'post')
@User.is_owner('post', lambda: abort(403))
def delete(post_id=None, post=None, user=None):
  post = post.get() if post else None
  if request.method == 'POST':
    if request.form.get('cancel'):
      return redirect(url_for('root'))
    if post:
      post.key.delete()
      return redirect(url_for('root'))
  if post:
    return render_template('delete.html', page=None, user=None, post=post)
  return abort(404)


@app.route("/signup/", methods=['GET', 'POST'])
# @sec.allow(lambda t: not t.get('usr'), lambda: redirect(url_for('root')))
@User.is_inactive(lambda: redirect(url_for('root')))
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
                          form_action='/signup/', pass_verified=pass_verified)


@app.route("/signin/", methods=['GET', 'POST'])
# @sec.allow(lambda t: not t.get('usr'), lambda: redirect(url_for('root')))
@User.is_inactive(lambda: redirect(url_for('root')))
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
                          form_action='/signin/', user_verified=user_verified,
                          pass_verified=pass_verified)


@app.route("/signout/", methods=['GET', 'POST'])
# @sec.allow(lambda t: t.get('usr'), lambda: redirect(url_for('signin')))
@User.is_active(lambda: redirect(url_for('signin')))
def signout(user=None):
  if request.method == 'POST':
    if request.form.get('cancel'):
      return redirect(url_for('root'))
    sec.token = {}
    return redirect(url_for('root'))
  return render_template('signout.html',
                          page=None, user=user, form_action='/signout/')


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
