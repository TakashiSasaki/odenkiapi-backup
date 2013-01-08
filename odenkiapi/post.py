from __future__ import unicode_literals, print_function
from model.Sender import GetSender
from model.RawData import putRawData
from model.Data import Data
from model.Metadata import putMetadata
from google.appengine.ext import db
from google.appengine.ext.webapp import RequestHandler, Response, Request
from urlparse import urlparse

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

class _Path(RequestHandler):
    def get(self):
        from urlparse import urlparse
        parsed_url = urlparse(self.request.url)
        self.response.out.write(parsed_url.path)

class _Params(RequestHandler):
    def get(self):
        assert isinstance(self.request, Request)
        from urlparse import urlparse
        parsed_url = urlparse(self.request.url)
        self.response.out.write(parsed_url.params)
        self.response.headers["a"] = "abc"

class _Query(RequestHandler):
    def get(self):
        from urlparse import urlparse
        parsed_url = urlparse(self.request.url)
        self.response.out.write(parsed_url.query)

class _Fragment(RequestHandler):
    def get(self):
        from urlparse import urlparse
        parsed_url = urlparse(self.request.url)
        self.response.out.write(parsed_url.fragment)

class _Body(RequestHandler):
    def get(self):
        self.response.out.write(self.request.body)

from google.appengine.ext.webapp import WSGIApplication
_wsgi_application= WSGIApplication([('/post', PostPage),
                                    ('/_Path', _Path),
                                    ('/_Params.*', _Params),
                                    ('/_Query', _Query),
                                    ('/_Fragment', _Fragment),
                                    ('/_Body', _Body)], 
                                   debug=True)

if __name__ == "__main__":
    from google.appengine.ext.webapp.util import run_wsgi_app
    run_wsgi_app(_wsgi_application)

from unittest import TestCase
class _MyTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        try:
            import webtest
        except ImportError:
            import setuptools.command.easy_install as easy_install
            easy_install.main(["WebTest"])
            exit()
        self.test_app = webtest.TestApp(_wsgi_application)
        from google.appengine.ext.testbed import Testbed
        self.testbed = Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        
    def tearDown(self):
        self.testbed.deactivate()
        TestCase.tearDown(self)

    def testGet(self):
        response = self.test_app.get("/post")
        import webtest
        self.assertIsInstance(response, webtest.TestResponse)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.headers["Content-Type"], 'text/plain')
    
    def test_Path(self):
        response = self.test_app.get("/_Path")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.headers["Content-Type"], 'text/html; charset=utf-8')
        self.assertEqual(response.body, '/_Path')
        
    def test_Params(self):
        response = self.test_app.request(b"/_Params;ppp?a=b&c=d#e", method=b"GET")
        self.assertEqual(response.headers["a"], "abc")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.headers["Content-Type"], 'text/html; charset=utf-8')
        self.assertEqual(response.body, "")

    def test_Fragment(self):
        response = self.test_app.request(b"/_Fragment?a=b&c=d#e", method=b"GET")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.headers["Content-Type"], 'text/html; charset=utf-8')
        self.assertEqual(response.body, "e")

    def test_Query(self):
        response = self.test_app.request(b"/_Query?a=b&c=d#e", method=b"GET")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.headers["Content-Type"], 'text/html; charset=utf-8')
        self.assertEqual(response.body, "a=b&c=d")

class _TestSemicolonInUrl(TestCase):
    
    def testUrlParse(self):
        """urlparse.urlparse recognizes the semicolon in the given path for http scheme."""
        self.assertEqual(urlparse("http://localhost/a/b/c;d").params, "d")
        self.assertEqual(urlparse("file://localhost/a/b/c;d").params, "")
        self.assertEqual(urlparse("file:///a/b/c;d").params, "")

    def testWebobRequest(self):
        """It shows a simple usage of WebOb Request class to create a blank request."""
        import webob
        request = webob.Request.blank("/a/b/c")
        self.assertEqual(request.url, "http://localhost/a/b/c")

    def testWebobRequestSemicolon(self):
        """The semicolon in the given path is URL-encoded UNEXPECTEDLY.""" 
        import webob
        request = webob.Request.blank("/a/b/c;d")
        self.assertEqual(request.url, "http://localhost/a/b/c%3Bd")
    