from flask import g
from google.appengine.ext import ndb
import re
from collections import namedtuple
from passlib.hash import pbkdf2_sha256 as pw_hasher
from functools import wraps
from . import BaseModel


Conf = namedtuple('Conf', ['PASSWORD_SECRET'])
conf = Conf('sssshhhhhhhhhhhh!')


def is_not_empty(prop, v):
  '''
  Check for empty values.
  '''
  if v:
    return v
  else:
    raise TypeError(s._name + ' cannot be empty.')


_re_is_username = re.compile('^[a-zA-Z0-9_-]{3,20}$')
_re_is_password = re.compile('^.{3,20}$')
_re_is_email = re.compile('^[\S]+@[\S]+.[\S]+$')


def is_username(prop, v):
  '''
  Check for values that pass username requirements.
  '''
  if v and _re_is_username.match(v):
    return v
  else:
    raise TypeError(prop._name + ' must be a valid username.')


def is_password(prop, v):
  '''
  Check for values that pass password requirements.
  '''
  if v and _re_is_password.match(v):
    return v
  else:
    raise TypeError(prop._name + ' must be a valid password.')


def is_email(prop, v):
  '''
  Check for values that pass email requirements.
  '''
  if v and _re_is_email.match(v):
    return v
  else:
    raise TypeError(prop._name + ' must be a valid email.')


class PasswordProperty(ndb.StringProperty):
  '''
  A custom password property with validation and verification.
  Passwords are hashed and compared using passlib.
  '''
  def _validate(self, value):
    if not isinstance(value, (str, unicode)):
      raise TypeError('expected a string, got %s' % repr(value))
    if not pw_hasher.identify(value):
      return pw_hasher.hash(is_password(self, value))

  def verify(cls, password, hash):
    return pw_hasher.verify(password, hash)


class User(BaseModel):
  '''
  User model for the app.
  Extends BaseModel.
  '''
  username = ndb.StringProperty(required=True, validator=is_username,
    indexed=True)
  password = PasswordProperty(required=True)
  email = ndb.StringProperty(required=True, validator=is_email)

  @classmethod
  def get_current(cls):
    '''
    Get the current user from cookies/tokens if possible.
    '''
    if g.security and g.security.token.get('usr'):
      user = ndb.Key(cls, g.security.token.get('uid')).get()
      if not user:
        g.security.token = {}
      return user
    return None

  @classmethod
  def is_available(cls):
    '''
    Decorator to provide user to wrapped function.
    '''
    def is_available_deco(fn):
      @wraps(fn)
      def is_available_handler(**kwargs):
        user = cls.get_current()
        kwargs['user'] = user
        return fn(**kwargs)
      return is_available_handler
    return is_available_deco

  @classmethod
  def is_active(cls, fail):
    '''
    Decorator to provide user to wrapped function.
    If not available calls fail handler.
    '''
    def is_active_deco(fn):
      @wraps(fn)
      def is_active_handler(**kwargs):
        user = cls.get_current()
        if not user:
          return fail()
        kwargs['user'] = user
        return fn(**kwargs)
      return is_active_handler
    return is_active_deco

  @classmethod
  def is_inactive(cls, fail):
    '''
    Decorator to ensure no user is signed-in.
    If a user is available, calls fail handler.
    '''
    def is_active_deco(fn):
      @wraps(fn)
      def is_active_handler(**kwargs):
        if g.security and g.security.token.get('usr'):
          return fail()
        return fn(**kwargs)
      return is_active_handler
    return is_active_deco

  @classmethod
  def is_owner(cls, what, fail):
    '''
    Decorator to provide user to wrapped function.
    Checks if the user owns the object in args identified by `what` arg.
    If not available or owner, fail handler is called.
    '''
    def is_owner_deco(fn):
      @wraps(fn)
      def is_owner_handler(**kwargs):
        user = cls.get_current()
        for entity in kwargs[what]:
          if not entity.key.parent() == user.key:
            return fail()
        kwargs['user'] = user
        return fn(**kwargs)
      return is_owner_handler
    return is_owner_deco

  @classmethod
  def is_author(cls, what, fail):
    '''
    Decorator to provide user to wrapped function.
    Checks if the user authored the object in args identified by `what` arg.
    If not available or author, fail handler is called.
    '''
    def is_author_deco(fn):
      @wraps(fn)
      def is_author_handler(**kwargs):
        user = cls.get_current()
        for entity in kwargs[what]:
          if not entity.author == user.key:
            return fail()
        kwargs['user'] = user
        return fn(**kwargs)
      return is_author_handler
    return is_author_deco

  @property
  def unique(self):
    '''
    Propery to check that the username is unique.
    '''
    try:
      val = getattr(self, '_unique', None)
      if val is None:
        self._unique = (False if User.query(User.username == self.username)
          .get() else True)
        val = self._unique
      return val
    except Exception as ex:
      print(ex)
      raise ex

  @unique.setter
  def unique(self, v):
    if v is None:
      self._unique = v

  # def valid(self, prop=None):
  #   isValid = False
  #   props = {prop: self._properties.get(prop)} if prop else self._properties
  #   for k, v in props.iteritems():
  #     if isinstance(v, ndb.Property):
  #       try:
  #         val = self._values.get(k)
  #         # print(k)
  #         if v._required and not val:
  #           # print(k, val, v._required)
  #           return False
  #         setattr(self, k, val)
  #         # print(k)
  #         isValid = True
  #       except Exception as ex:
  #         # print(ex)
  #         return False
  #   return isValid

  # def fill(self, **kwargs):
  #   # print('populate:')
  #   # for k, v in kwargs.iteritems():
  #   for k in self._properties:
  #     v = kwargs.get(k)
  #     if v:
  #       self._values[k] = v
