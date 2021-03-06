from flask import Flask, request, render_template, redirect, url_for, abort
from google.appengine.ext import ndb
from google.appengine.ext.db import BadRequestError
from models.auth import User
from models.blog import BlogPost, BlogComment
from utils.security import Security
from functools import wraps
import mistune


app = Flask(__name__, template_folder="views",
            static_folder='bld', static_url_path='/static')
app.debug = True
sec = Security(app, 'shh')
md = mistune.Markdown()
app.jinja_env.filters['md'] = md  # Add markdown filter.


def is_form_cancelled(redir):
  def is_form_cancelled_deco(fn):
    @wraps(fn)
    def is_form_cancelled_handler(**kwargs):
      if request.method == 'POST':
        if request.form.get('cancel'):
          return redir()
      return fn(**kwargs)
    return is_form_cancelled_handler
  return is_form_cancelled_deco


@app.route("/", defaults={'offset': 0})
@app.route("/<int:offset>")
@BlogPost.q('ORDER BY created DESC LIMIT 10 OFFSET {{offset}}', 'posts')
@User.is_available()
def root(offset=0, posts=None, user=None):
  '''
  View a list of posts.
  '''
  user = user or None
  posts = posts or None
  next = offset + 10
  prev = offset - 10 if offset >= 10 else 0
  return render_template('index.html', page=None, user=user,
                            posts=posts, next=next, prev=prev)


@app.route("/view/<string:post_id>", methods=['GET', 'POST'])
@app.route("/view/<string:post_id>/<string:comment_id>",
           methods=['GET', 'POST'])
@BlogPost.q('WHERE uid = \'{{post_id}}\'', 'post')
@BlogComment.q('WHERE ANCESTOR IS {{post.get().key|safe}}', 'comments')
@BlogComment.q('WHERE uid = \'{{comment_id}}\'', 'comment')
@User.is_available()
def view(post_id=None, comment_id=None,
  comment=None, post=None, comments=None, user=None):
  '''
  View and comment on a post.
  '''
  if request.form.get('cancel'):
    return redirect(url_for('view', post_id=post_id) + '#comments')

  user = user or None
  post = post.get() if post else None
  comments = comments or None
  comment = comment.get() if comment else None
  if user and post and request.method == 'POST':
    comment = comment or BlogComment(parent=post.key)
    comment.fill(content=request.form.get('content', None), author=user.key)
    if not comment.empty('content'):
      comment.put()
      return redirect(url_for('view', post_id=post_id) + '#' + comment.uid)
    else:
      return render_template('view.html', page=None, user=user,
                          post=post, comments=comments,
                          comment_id=comment_id)
  elif post:
    return render_template('view.html', page=None, user=user,
                            post=post, comments=comments,
                            comment_id=comment_id)
  else:
    return abort(404)


@app.route("/fave/<string:post_id>", methods=['POST'])
@User.is_active(lambda: abort(403))
@BlogPost.q('WHERE uid = \'{{post_id}}\'', 'post')
def fave(post_id=None, post=None, user=None):
  '''
  Post to this route with a user and post it, and fave it.
  '''
  user = user or None
  post = post.get() if post else None
  res = None
  if post:
    if post.key.parent() == user.key:
      return abort(403)
    faved = post.faved
    try:
      faved.remove(user.uid)
      res = 'remove'
    except ValueError as ex:
      faved.append(user.uid)
      res = 'add'
    post.faved = faved
    post.put()
    return res
  else:
    return abort(404)


@app.route("/edit/", defaults={'post_id': ''}, methods=['GET', 'POST'])
@app.route("/edit/<string:post_id>", methods=['GET', 'POST'])
@is_form_cancelled(
  lambda: redirect(request.args.get('next', None) or url_for('root')))
@User.is_active(lambda: redirect(url_for('signin')))
@BlogPost.q(
  'WHERE ANCESTOR IS {{user.key|safe}} AND uid = \'{{post_id}}\'', 'post')
@User.is_owner('post', lambda: abort(403))
def edit(post_id=None, post=None, user=None):
  '''
  Create or edit a post.
  '''
  user = user or None
  post = post.get() if post else None
  if request.method == 'POST':
    post = post or BlogPost(parent=user.key)
    post.fill(**request.form.to_dict())
    if not post.empty('subject', 'content'):
      try:
        key = post.put()
        return redirect(url_for('edit', post_id=post.uid))
      except Exception as ex:
        print('post crud error', ex)
        return abort(500)
  return render_template('edit.html', page=None, user=user, post=post)


@app.route("/delete/<string:post_id>", methods=['GET', 'POST'])
@is_form_cancelled(
  lambda: redirect(request.args.get('next', None) or url_for('root')))
@User.is_active(lambda: redirect(url_for('signin')))
@BlogPost.q('WHERE uid = \'{{post_id}}\'', 'post')
@User.is_owner('post', lambda: abort(403))
def delete(post_id=None, post=None, user=None):
  '''
  Delete a post.
  '''
  post = post.get() if post else None
  next = request.args.get('next', None)
  if request.method == 'POST':
    if post:
      post.key.delete()
      return redirect(url_for('root'))
  if post:
    return render_template('delete.html', page=None, user=None,
                           post=post)
  return abort(404)


@app.route("/delete/<string:post_id>/<string:comment_id>",
  methods=['GET', 'POST'])
@is_form_cancelled(
  lambda: redirect(request.args.get('next', None) or url_for('root')))
@User.is_active(lambda: redirect(url_for('signin')))
@BlogComment.q('WHERE uid = \'{{comment_id}}\'', 'comment')
@User.is_author('comment', lambda: abort(403))
def delete_comment(post_id=None, comment_id=None,
  post=None, comment=None, user=None):
  '''
  Delete a post.
  '''
  comment = comment.get() if comment else None
  next = request.args.get('next', None)
  if request.method == 'POST':
    if comment:
      comment.key.delete()
      return redirect(url_for('view', post_id=post_id) + '#comments')
  if comment:
    return render_template('delete.html', page=None, user=None,
                           post=None, comment=comment)
  return abort(404)


@app.route("/signup/", methods=['GET', 'POST'])
@is_form_cancelled(
  lambda: redirect(request.args.get('next', None) or url_for('root')))
@User.is_inactive(lambda: redirect(url_for('root')))
def signup():
  '''
  Register a new user.
  '''
  user = None
  pass_verified = None
  next = request.args.get('next', None)
  if request.method == 'POST':
    try:
      user = User()
      user.fill(**request.form.to_dict())
      pass_verified = request.form.get('verify') == request.form.get('password')  # NOQA
      if user.valid() and user.unique and pass_verified:
        user.put()
        sec.token = {'usr': user.username, 'uid': user.uid}
        return redirect(next or url_for('root'))
    except Exception as ex:
      print('bad user')
      print(ex)
      return abort(500)
  return render_template('signup.html',
                          page=None, user=user,
                          form_action=url_for('signup', next=next),
                          next=next,
                          pass_verified=pass_verified)


@app.route("/signin/", methods=['GET', 'POST'])
@is_form_cancelled(
  lambda: redirect(request.args.get('next', None) or url_for('root')))
@User.is_inactive(lambda: redirect(url_for('root')))
def signin():
  '''
  Verify and signin a user.
  '''
  user = None
  user_verified = False
  pass_verified = False
  next = request.args.get('next', None)
  if request.method == 'POST':
    try:
      user = User.query(User.username == request.form.get('username', '')).get()  # NOQA
    except Exception as ex:
      pass
    user_verified = True if user else False
    if (user and user.password and
      User.password.verify(request.form.get('password'), user.password)):
      sec.token = {'usr': user.username, 'uid': user.uid}
      pass_verified = True
      return redirect(next or url_for('root'))
    else:
      user = User()
      user.fill(username=request.form.get('username'))
  return render_template('signin.html',
                          page=None, user=user,
                          form_action=url_for('signin', next=next),
                          next=next,
                          user_verified=user_verified,
                          pass_verified=pass_verified)


@app.route("/signout/", methods=['GET', 'POST'])
@is_form_cancelled(
  lambda: redirect(request.args.get('next', None) or url_for('root')))
@User.is_active(lambda: redirect(url_for('signin')))
def signout(user=None):
  '''
  Signout the current user.
  '''
  next = request.args.get('next', None)
  if request.method == 'POST':
    sec.token = {}
    return redirect(next or url_for('root'))
  return render_template('signout.html',
                          page=None, user=user,
                          form_action=url_for('signout', next=next),
                          next=next)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
