# this code was from https://github.com/dound/gae-sessions/blob/master/README.markdown
from __future__ import unicode_literals, print_function
import logging as _logging
_logging.getLogger().setLevel(_logging.DEBUG)

import sys as _sys
_sys.setrecursionlimit = 5

def webapp_add_wsgi_middleware(app):
    from gaesessions import SessionMiddleware
    from credentials import SESSION_SALT
    newapp = SessionMiddleware(app, cookie_key=SESSION_SALT)

    # Appstats is temporarily removed to prevent the following message
    # "Full proto too large to save, cleared variables."
    #from google.appengine.ext.appstats import recording
    #newapp = recording.appstats_wsgi_middleware(newapp)

    return newapp
