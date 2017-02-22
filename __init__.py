from flask import Flask, request, render_template, redirect, url_for
from models.auth import User
from utils.security import Security


app = Flask(__name__, template_folder="views",
            static_folder='bld', static_url_path='/static')
app.debug = True
sec = Security(app, 'shh')


@app.route("/")
def root():
  user = None
  print(repr(sec.token))
  if sec.token.get('usr'):
    print(sec.token.get('usr'))
    user = User()
    user.fill(username=sec.token.get('usr'))
  return render_template('index.html', page=None, user=user)


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
