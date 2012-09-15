from __future__ import unicode_literals, print_function
#def runWsgiApp(request_handler, path=None):
#    """a wrapper to run single RequestHandler."""
#    from google.appengine.ext.webapp import WSGIApplication
#    from google.appengine.ext.webapp.util import run_wsgi_app
#    if path is None:
#        path = '/' + getMainModuleName()
#    application = WSGIApplication([(path, request_handler)], debug=True)
#    run_wsgi_app(application)
    
from google.appengine.ext.webapp import WSGIApplication as _WSGIApplication
class WSGIApplication(_WSGIApplication):
    def __init__(self, *args, **keys):
        _WSGIApplication.__init__(self, *args, **keys)
        
from google.appengine.ext.webapp.util import run_wsgi_app as _run_wsgi_app
def run_wsgi_app(application_or_mapping):
    """This wrapped version of run_wsgi_app accepts an instance of either WSGIApplication or list"""
    if isinstance(application_or_mapping, list):
        application_or_mapping = WSGIApplication(application_or_mapping)
    from google.appengine.ext import ndb
    _run_wsgi_app(ndb.toplevel(application_or_mapping))

RPC_ERROR_USER_AGENT_DOES_NOT_ACCEPT_HTML = 1


#from JsonRpc import JsonRpc
#from GoogleUser import getGoogleUser, GoogleUser
#from DateTimeUtil import toRfcFormat, fromRfcFormat, getIfModifiedSince, getNow
#from MethodsHandler import MethodsHandler
#from OdenkiSession import OdenkiSession
from JsonRpcDispatcher import JsonRpcDispatcher
