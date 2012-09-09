from json import JSONEncoder as _JSONEncoder
from gaesessions import Session
from gdata.gauth import OAuthHmacToken 

from json import dumps as _dumps
def dumps(d):
    return _dumps(d, indent=4, cls=JSONEncoder)

class JSONEncoder(_JSONEncoder):
    def default(self,o):
        if isinstance(o, Session):
            return str(o.sid)
        if isinstance(o, OAuthHmacToken):
            return o.token
        return JSONEncoder.default(self, o)
