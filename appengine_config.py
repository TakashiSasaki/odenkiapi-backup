# this code was from https://github.com/dound/gae-sessions/blob/master/README.markdown
from __future__ import unicode_literals, print_function
def webapp_add_wsgi_middleware(app):
    from gaesessions import SessionMiddleware
    from credentials import SESSION_SALT
    newapp = SessionMiddleware(app, cookie_key=SESSION_SALT)

    from google.appengine.ext.appstats import recording
    newapp = recording.appstats_wsgi_middleware(newapp)

    return newapp
