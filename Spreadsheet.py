from MyRequestHandler import MyRequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication

class _RequestHandler(MyRequestHandler):
    def get(self):
        self.writeWithTemplate({}, "Spreadsheet")

if __name__ == "__main__":
    application = WSGIApplication([('/Spreadsheet', _RequestHandler)], debug=True)
    run_wsgi_app(application)
