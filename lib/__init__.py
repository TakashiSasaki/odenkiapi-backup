#from lib.debug import *
#from logging import debug, DEBUG, getLogger
#getLogger().setLevel(DEBUG)

def getMainModule():
    from sys import modules
    return modules["__main__"]
 
def getMainModuleName():
    from os.path import basename, splitext
    b = basename(getMainModule().__file__)
    (stem, ext) = splitext(b)
    return stem

def runWsgiApp(request_handler, path=None):
    """a wrapper to run single RequestHandler."""
    from google.appengine.ext.webapp import WSGIApplication
    from google.appengine.ext.webapp.util import run_wsgi_app
    if path is None:
        path = '/' + getMainModuleName()
    application = WSGIApplication([(path, request_handler)], debug=True)
    run_wsgi_app(application)

RPC_ERROR_USER_AGENT_DOES_NOT_ACCEPT_HTML = 1

from simplejson import dumps as _dumps
def dumps(d):
    return _dumps(d, indent=4)

#from JsonRpc import JsonRpc
#from GoogleUser import getGoogleUser, GoogleUser
#from DateTimeUtil import toRfcFormat, fromRfcFormat, getIfModifiedSince, getNow
#from MethodsHandler import MethodsHandler
#from OdenkiSession import OdenkiSession

def isEqualIfExists(o1, o2, a):
    if not hasattr(o1, a) and not hasattr(o2, a): return True
    if not hasattr(o1, a): return False
    if not hasattr(o2, a): return False
    if o1.a != o2.a: return False
    return True
