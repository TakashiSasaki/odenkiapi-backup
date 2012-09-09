# this code was from https://github.com/dound/gae-sessions/blob/master/README.markdown

from gaesessions import SessionMiddleware
from credentials import SESSION_SALT
def webapp_add_wsgi_middleware(app):
    newapp = SessionMiddleware(app, cookie_key=SESSION_SALT)
    return newapp

import logging as _logging
_logging.getLogger().setLevel(_logging.DEBUG)


import sys as _sys
_sys.setrecursionlimit = 5
