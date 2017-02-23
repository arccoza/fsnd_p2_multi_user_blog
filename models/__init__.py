from google.appengine.ext import ndb


class BaseModel(ndb.Model):
  created = ndb.DateTimeProperty(auto_now_add=True)
  updated = ndb.DateTimeProperty(auto_now=True)

  def empty(self, *args):
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
