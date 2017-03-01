from google.appengine.ext import ndb
from .auth import User
from . import BaseModel


class BlogPost(BaseModel):
  author = ndb.KeyProperty(kind=User)
  subject = ndb.StringProperty()
  content = ndb.TextProperty()
  faved = ndb.StringProperty(repeated=True)


class BlogComment(BaseModel):
  author = ndb.KeyProperty(kind=User)
  subject = ndb.StringProperty()
  content = ndb.StringProperty()
