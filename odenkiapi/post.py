from __future__ import unicode_literals, print_function
from model.Sender import GetSender
from model.RawData import putRawData
from model.Data import Data
from model.Metadata import putMetadata
from google.appengine.ext import db
from google.appengine.ext.webapp import RequestHandler, Response

class PostPage(RequestHandler):

    def get(self):
        self.sender = GetSender(self.request)
        self.raw_data = putRawData(self.request)
        #self.data_list = putDataList(self.request)
        self.data_list = Data.storeRequest(self.request)
        self.metadata = putMetadata(self.sender, self.raw_data, self.data_list)
        
        assert isinstance(self.response, Response)
        self.response.headers['Content-Type'] = "text/plain"
        for key in self.data_list:
            data = db.get(key)
            self.response.out.write("field:" + data.field + " string:" + data.string + "\n")

    def post(self):
        #logging.info("body="+self.request.body)
        self.get()


from google.appengine.ext.webapp import WSGIApplication
wsgi_application= WSGIApplication([('/post', PostPage)], debug=True)

if __name__ == "__main__":
    from google.appengine.ext.webapp.util import run_wsgi_app
    run_wsgi_app(wsgi_application)

import unittest

class MyTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        try:
            import webtest
        except ImportError:
            import setuptools.command.easy_install as easy_install
            easy_install.main(["WebTest"])
            exit()
        self.test_app = webtest.TestApp(wsgi_application)
        from google.appengine.ext.testbed import Testbed
        self.testbed = Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        
    def tearDown(self):
        self.testbed.deactivate()
        unittest.TestCase.tearDown(self)

    def testGet(self):
        response = self.test_app.get("/post")
        import webtest
        self.assertIsInstance(response, webtest.TestResponse)
        self.assertEqual(response.status, "200 OK")
