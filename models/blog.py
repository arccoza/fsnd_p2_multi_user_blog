from google.appengine.ext import ndb
from . import BaseModel


class BlogPost(BaseModel):
  subject = ndb.StringProperty()
  content = ndb.TextProperty()


class BlogComment(BaseModel):
  subject = ndb.StringProperty()
  content = ndb.StringProperty()
