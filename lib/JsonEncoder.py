from json import JSONEncoder as _JSONEncoder
from gaesessions import Session
from gdata.gauth import OAuthHmacToken
from datetime import datetime 
from google.appengine.ext import ndb
from google.appengine.ext import db

from json import dumps as _dumps
from model.NdbModel import NdbModel
def dumps(d):
    return _dumps(d, indent=4, cls=JSONEncoder)

class JSONEncoder(_JSONEncoder):
    def default(self,o):
        if isinstance(o, Session):
            return str(o.sid)
        if isinstance(o, OAuthHmacToken):
            return o.token
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, ndb.Key):
            assert isinstance(o, ndb.Key)
            return unicode(o)
        if isinstance(o, db.Key):
            assert isinstance(o, db.Key)
            return unicode(o)
        if isinstance(o, NdbModel):
            return o.to_dict()
        return JSONEncoder.default(self, o)
