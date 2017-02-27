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
  if v:
    return v
  else:
    raise TypeError(s._name + ' cannot be empty.')


_re_is_username = re.compile('^[a-zA-Z0-9_-]{3,20}$')
_re_is_password = re.compile('^.{3,20}$')
_re_is_email = re.compile('^[\S]+@[\S]+.[\S]+$')


def is_username(prop, v):
  if v and _re_is_username.match(v):
    return v
  else:
    raise TypeError(prop._name + ' must be a valid username.')


def is_password(prop, v):
  # print('is_password: ', v, _re_is_password.match(v))
  if v and _re_is_password.match(v):
    return v
  else:
    raise TypeError(prop._name + ' must be a valid password.')


def is_email(prop, v):
  # print('is_email: ', v, _re_is_email.match(v))
  if v and _re_is_email.match(v):
    return v
  else:
    raise TypeError(prop._name + ' must be a valid email.')


class PasswordProperty(ndb.StringProperty):
  def _validate(self, value):
    if not isinstance(value, (str, unicode)):
      raise TypeError('expected a string, got %s' % repr(value))
    if not pw_hasher.identify(value):
      return pw_hasher.hash(is_password(self, value))

  def verify(cls, password, hash):
    # print(password, hash)
    return pw_hasher.verify(password, hash)


class User(BaseModel):
  username = ndb.StringProperty(required=True, validator=is_username)
  password = PasswordProperty(required=True)
  email = ndb.StringProperty(required=True, validator=is_email)

  @classmethod
  def get_current(cls):
    if g.security and g.security.token.get('usr'):
      user = cls.query(cls.username == g.security.token.get('usr')).get()
      if not user:
        g.security.token = {}
      return user
    return None

  @classmethod
  def is_available(cls):
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

  @property
  def unique(self):
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

  def valid(self, prop=None):
    isValid = False
    props = {prop: self._properties.get(prop)} if prop else self._properties
    for k, v in props.iteritems():
      if isinstance(v, ndb.Property):
        try:
          val = self._values.get(k)
          # print(k)
          if v._required and not val:
            # print(k, val, v._required)
            return False
          setattr(self, k, val)
          # print(k)
          isValid = True
        except Exception as ex:
          # print(ex)
          return False
    return isValid

  def fill(self, **kwargs):
    # print('populate:')
    # for k, v in kwargs.iteritems():
    for k in self._properties:
      v = kwargs.get(k)
      if v:
        self._values[k] = v
