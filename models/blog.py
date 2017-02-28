from google.appengine.ext import ndb
from . import BaseModel


class BlogPost(BaseModel):
  subject = ndb.StringProperty()
  content = ndb.TextProperty()
  faved = ndb.StringProperty(repeated=True)


class BlogComment(BaseModel):
  subject = ndb.StringProperty()
  content = ndb.StringProperty()
