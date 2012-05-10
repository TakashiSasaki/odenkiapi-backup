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

def runWsgiApp(request_handler):
    from google.appengine.ext.webapp import WSGIApplication
    from google.appengine.ext.webapp.util import run_wsgi_app
    application = WSGIApplication([('/' + getMainModuleName(),
                                    request_handler)], debug=True)
    run_wsgi_app(application)

