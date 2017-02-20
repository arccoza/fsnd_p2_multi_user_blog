from flask import Flask, g, Blueprint, current_app, request, make_response, render_template, redirect, url_for, abort
from jinja2 import TemplateNotFound
from models.auth import User
from utils.security import Security


auth_pages = Blueprint('auth', __name__, template_folder='views')
sec = Security(auth_pages, 'shh')


# # sec = Security()
# @auth_pages.record
# def prep(setup_state):
#   print('record')
#   # sec.init(setup_state.app, 'shh')

#   # @setup_state.app.before_request
#   # def hip():
#   #   sec.token['username'] = 'bob'


@auth_pages.route('/signup', methods=['GET', 'POST'])
@sec.allow(lambda t: not t.get('username'), lambda: redirect(url_for('auth.welcome')))
def signup():
  user = None
  pass_verified = None
  if request.method == 'POST':
    try:
      user = User()
      user.fill(**request.form.to_dict())
      pass_verified = request.form.get('verify') == request.form.get('password')
      if user.valid() and user.unique and pass_verified:
        user.put()
        sec.token = {'username': user.username}
        return redirect(url_for('auth.welcome'))
    except Exception as ex:
      print('bad user')
      print(ex)
  try:
    return render_template('signup.html', auth=user, pass_verified=pass_verified)
  except TemplateNotFound:
    abort(404)


@auth_pages.route('/login', methods=['GET', 'POST'])
@sec.allow(lambda t: not t.get('username'), lambda: redirect(url_for('auth.welcome')))
def login():
  user = None
  pass_verified = False
  if request.method == 'POST':
    user = User.query(User.username == request.form.get('username')).get()
    if not user:
      user = User()
      user.fill(username=request.form.get('username'))
    if (user and user.password and
      User.password.verify(request.form.get('password'), user.password)):
      sec.token = {'username': user.username}
      pass_verified = True
      return redirect(url_for('auth.welcome'))
  try:
    return render_template('login.html',
                            auth=user, pass_verified=pass_verified)
  except TemplateNotFound:
    abort(404)


@auth_pages.route('/logout')
@sec.allow(lambda t: t.get('username'), lambda: redirect(url_for('auth.login')))
def logout():
  sec.token = {}
  return redirect(url_for('auth.login'))


@auth_pages.route('/welcome')
@sec.allow(lambda t: t.get('username'), lambda: redirect(url_for('auth.login')))
def welcome():
  return render_template('welcome.html', username=sec.token.get('username'))
