from model.Sender import GetSender
from model.RawData import putRawData
from model.Data import Data
from model.Metadata import putMetadata
from google.appengine.ext import db
from google.appengine.ext.webapp import RequestHandler

class PostPage(RequestHandler):

    def get(self):
        self.sender = GetSender(self.request)
        self.raw_data = putRawData(self.request)
        #self.data_list = putDataList(self.request)
        self.data_list = Data.storeRequest(self.request)
        self.metadata = putMetadata(self.sender, self.raw_data, self.data_list)
        
        self.response.headers['Content-Type'] = "text/plain"
        for key in self.data_list:
            data = db.get(key)
            self.response.out.write("field:" + data.field + " string:" + data.string + "\n")

    def post(self):
        #logging.info("body="+self.request.body)
        self.get()

if __name__ == "__main__":
    from google.appengine.ext.webapp import WSGIApplication
    application = WSGIApplication([('/post', PostPage)], debug=True)
    from google.appengine.ext.webapp.util import run_wsgi_app
    run_wsgi_app(application)
