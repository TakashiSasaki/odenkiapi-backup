from lib.JsonRpc import JsonRpcDispatcher, JsonRpcResponse
from model.SenderNdb import Sender

class _Range(JsonRpcDispatcher):
#    @ndb.toplevel
#    def get(self):
#        path_info = self.request.path_info.split("/")
#        start = int(path_info[3])
#        end = int(path_info[4])
#        q = RawData.queryPeriod(start, end)
#        
#        for raw_data_key in q.fetch(keys_only=True):
#            self.response.out.write(str(raw_data_key.get()))
            
    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = self.request.path_info.split("/")
        start = int(path_info[3])
        end = int(path_info[4])
        query = Sender.queryRange(start, end)
        keys = query.fetch(keys_only=True)
        for key in keys:
            sender = key.get()
            assert isinstance(sender, Sender)
            jresponse.addResult(sender.getFields())
        
class _Recent(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        query = Sender.queryRecent()
        keys = query.fetch(keys_only=True)
        for key in keys:
            sender = key.get()
            assert isinstance(sender, Sender)
            jresponse.addResult(sender)

if __name__ == "__main__":
    mapping = []
    mapping.append(('/record/Sender/[0-9]+/[0-9]+', _Range))
    mapping.append(('/record/Sender', _Recent))
    from lib import WSGIApplication
    application = WSGIApplication(mapping)
    from lib import run_wsgi_app
    run_wsgi_app(application)
