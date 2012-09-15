from __future__ import unicode_literals, print_function
from json import JSONEncoder as _JSONEncoder
from gaesessions import Session
from gdata.gauth import OAuthHmacToken
from datetime import datetime 
from google.appengine.ext import ndb
from google.appengine.ext import db
from logging import debug
from model.Columns import Columns

from model.NdbModel import NdbModel

class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if isinstance(o, Session):
            return str(o.sid)
        if isinstance(o, OAuthHmacToken):
            return o.token
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, ndb.Key):
            assert isinstance(o, ndb.Key)
            debug("encoding ndb.Key %s to JSON" % o)
            entity = o.get()
            if entity is None: return None
            return unicode(o.get().to_dict())
        if isinstance(o, db.Key):
            assert isinstance(o, db.Key)
            debug("encoding db.Key %s to JSON" % o)
            return unicode(o)
        if isinstance(o, NdbModel):
            return o.to_dict()
            debug("encoding NdbModel %s to JSON" % o)
        if isinstance(o, Columns):
            assert isinstance(o, Columns)
            debug("encoding Columns %s to JSON" % o)
            return o.getDataTableCols()
        debug("encoding unknown object %s, %s " % (type(o), o))
        return _JSONEncoder.default(self, o)
