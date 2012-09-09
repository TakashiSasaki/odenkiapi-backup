from lib.JsonRpc import JsonRpcDispatcher, JsonRpcResponse
from model.MetadataNdb import Metadata

class _Recent(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        query = Metadata.queryRecent()
        keys = query.fetch(keys_only=True)
        for key in keys:
            metadata = key.get()
            assert isinstance(metadata, Metadata)
            jresponse.addResult(metadata.getFields())
    
class _Range(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        pass

if __name__ == "__main__":
    mapping = []
    mapping.append(("/record/Metadata", _Recent))
    mapping.append(("/record/Metadata/[0-9]+/[0-9]+", _Range))
    from google.appengine.ext.webapp import WSGIApplication
    application = WSGIApplication(mapping, debug=True)
    from google.appengine.ext.webapp.util import run_wsgi_app
    run_wsgi_app(application)
    
