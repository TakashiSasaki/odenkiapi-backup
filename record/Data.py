from lib.JsonRpc import JsonRpcDispatcher
from urlparse import urlparse
from model.DataNdb import Data
from google.appengine.ext import ndb
from logging import debug

class DataTestHandler(JsonRpcDispatcher):

    def get(self):
        query_string = urlparse(self.request.url)[4]
        debug(query_string)
        
        if len(query_string)>0:
            keys = Data.putParams(query_string)
            self.response.out.write("keys = %s" % keys)
            return
        
        query = Data.getByDataIdDecending()
        keys = query.fetch(keys_only=True)
        for k in keys:
            assert isinstance(k, ndb.Key)
            e = k.get()
            assert isinstance(e, Data)
            self.response.out.write("%s, %s, %s \n" % (e.dataId, e.field, e.string))
        self.response.content_type="text/plain"

if __name__ == "__main__":
    from google.appengine.ext.webapp import WSGIApplication
    mapping = [("/api/data", DataTestHandler)]
    application = WSGIApplication(mapping, debug=True)
    from google.appengine.ext.webapp.util import run_wsgi_app
    run_wsgi_app(application)
