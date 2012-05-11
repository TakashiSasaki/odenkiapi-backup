from logging import debug, DEBUG, getLogger
getLogger().setLevel(DEBUG)

def getMainModule():
    from sys import modules
    return modules["__main__"]
 
def getMainModuleName():
    from os.path import basename, splitext
    b = basename(getMainModule().__file__)
    (stem, ext) = splitext(b)
    return stem

def runWsgiApp(request_handler, path):
    debug("MyRequestHandler main")
    from google.appengine.ext.webapp import WSGIApplication
    from google.appengine.ext.webapp.util import run_wsgi_app
    if path is None:
        path = '/' + getMainModuleName()
    application = WSGIApplication([(path, request_handler)], debug=True)

    run_wsgi_app(application)

