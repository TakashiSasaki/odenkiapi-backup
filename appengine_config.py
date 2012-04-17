# this code was from https://github.com/dound/gae-sessions/blob/master/README.markdown

from gaesessions import SessionMiddleware
def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(app, cookie_key="a random and long string")
    return app
