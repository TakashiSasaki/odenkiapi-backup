# this code was from https://github.com/dound/gae-sessions/blob/master/README.markdown

from gaesessions import SessionMiddleware
def webapp_add_wsgi_middleware(app):
    newapp = SessionMiddleware(app, cookie_key="oipsadmcfoiuihiuohioh9088uk90u89ku8hiojop,jpoj,opajf932408hga")
    return newapp
