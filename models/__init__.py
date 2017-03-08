from flask import render_template_string
from google.appengine.ext import ndb
from functools import wraps
from utils.cuid import cuid


class UidProperty(ndb.StringProperty):
  # def __init__(self, *args, **kwargs):
  #   super(UidProperty, self).__init__(*args, **kwargs)
  #   print(cuid)

  def _validate(self, value):
    if not isinstance(value, (str, unicode)):
      raise TypeError('expected a string, got %s' % repr(value))
    return value if value and value[0] == 'c' else cuid()


class BaseModel(ndb.Model):
  '''
  The base model class for all models in this app.
  This model generates unique keys independent of GAE datastore.
  '''
  uid = UidProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  updated = ndb.DateTimeProperty(auto_now=True)

  def __init__(self, *args, **kwargs):
    uid = cuid()
    if kwargs.get('key'):
      flat = list(kwargs['key'].flat())
      flat[-1] = uid
      ndb.Key(*flat)
      # print('flat: ', flat)
    else:
      kwargs['id'] = uid
    super(BaseModel, self).__init__(*args, **kwargs)
    self.uid = self.uid or uid
    # self.key = ndb.Key(self._get_kind(), self.uid)

  @classmethod
  def q(cls, query, kw_out):
    '''
    A query decorator that passes the query cursor onto the wrapped function.
    '''
    def q_deco(fn):
      @wraps(fn)
      def q_handler(**kwargs):
        # kwargs[kw_out] = cls.gql(query % kwargs)
        # print(kwargs)
        kwargs[kw_out] = cls.gql(render_template_string(query, **kwargs))
        return fn(**kwargs)
      return q_handler
    return q_deco

  def empty(self, *args):
    '''
    Check if the provided property names have an empty value.
    Fails on the first empty value.
    '''
    args = args or self._properties
    for prop in args:
      if not getattr(self, prop):
        return True
    return False

  @property
  def unique(self):
    try:
      if getattr(self, '_unique', None) is None:
        self._unique = False if self._unique_query.get() else True
      return self._unique
    except Exception as ex:
      print(ex)
      raise ex

  @unique.setter
  def unique(self, v):
    if v is None:
      self._unique = v

  def valid(self, prop=None):
    '''
    Check if the model is valid,
    or provide a property name and check if it is valid.
    '''
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
    '''
    Fill the model with the keyword values that match prop names.
    Does not trigger validation.
    '''
    # print('populate:')
    # for k, v in kwargs.iteritems():
    for k in self._properties:
      v = kwargs.get(k)
      if v:
        self._values[k] = v
