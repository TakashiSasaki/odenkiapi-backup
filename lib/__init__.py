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

def runWsgiApp(request_handler, path):
    from google.appengine.ext.webapp import WSGIApplication
    from google.appengine.ext.webapp.util import run_wsgi_app
    if path is None:
        path = '/' + getMainModuleName()
    application = WSGIApplication([(path, request_handler)], debug=True)

    run_wsgi_app(application)

RPC_ERROR_USER_AGENT_DOES_NOT_ACCEPT_HTML = 1

import logging as _logging
from logging import debug 
_logging.getLogger().setLevel(_logging.DEBUG)

from JsonRpc import JsonRpc
from GoogleUser import getGoogleUser, GoogleUser
from DateTimeUtil import toRfcFormat, fromRfcFormat, getIfModifiedSince, getNow
from MethodsHandler import MethodsHandler
from OdenkiSession import OdenkiSession