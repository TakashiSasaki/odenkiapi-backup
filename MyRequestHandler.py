from os import environ
environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.api import memcache
CACHE_BACKEND = 'memcached:///'
from google.appengine.ext.webapp import RequestHandler, template
from datetime import datetime
from simplejson import dumps, load, loads, JSONDecodeError
from google.appengine.api.users import get_current_user, create_login_url, create_logout_url
from logging import debug, getLogger, DEBUG
from encodings.base64_codec import base64_decode
getLogger().setLevel(DEBUG)

JSON_RPC_ERROR_PARSE_ERROR = -32700
JSON_RPC_ERROR_INVALID_REQUEST = -32600
JSON_RPC_ERROR_METHOD_NOT_FOUND = -32601
JSON_RPC_ERROR_INVALID_PARAMS = -32602
JSON_RPC_ERROR_INTERNAL_ERROR = -32603
JSON_RPC_ERROR_SERVER_ERROR_RESERVED_MAX = -32000
JSON_RPC_ERROR_SERVER_ERROR_RESERVED_MIN = -32099

def toHttpStatus(json_rpc_error_code):
    if json_rpc_error_code == JSON_RPC_ERROR_PARSE_ERROR:
        return 500
    if json_rpc_error_code == JSON_RPC_ERROR_INVALID_REQUEST:
        return 400
    if json_rpc_error_code == JSON_RPC_ERROR_METHOD_NOT_FOUND:
        return 404
    if json_rpc_error_code == JSON_RPC_ERROR_INVALID_PARAMS:
        return 500
    if json_rpc_error_code == JSON_RPC_ERROR_INTERNAL_ERROR:
        return 500
    if json_rpc_error_code >= JSON_RPC_ERROR_SERVER_ERROR_RESERVED_MIN and json_rpc_error_code <= JSON_RPC_ERROR_SERVER_ERROR_RESERVED_MAX:
        return 500
    return None

def getMainModule():
    from sys import modules
    return modules["__main__"]
 
def getMainModuleName():
    from os.path import basename, splitext
    b = basename(getMainModule().__file__)
    (stem, ext) = splitext(b)
    return stem

def getMainModuleRequestHandler():
    return getMainModule()._RequestHandler
    
class MyRequestHandler(RequestHandler):
    __slots__ = ["jsonRequest", "jsonResponse"]
    
    def hasNoParam(self):
        return True if self.request.params.items().__len__() == 0 else False
        
    def getTimeStamp(self):
        version_id = self.request.environ["CURRENT_VERSION_ID"].split('.')[1]
        timestamp = long(version_id) / pow(2, 28)
        return timestamp
    
    def getTimeStampString(self):
        timestamp = self.getTimeStamp()
        return datetime.fromtimestamp(timestamp).strftime("%Y/%m/%d %X UTC")

    def getVersion(self):
        return self.request.environ["CURRENT_VERSION_ID"].split('.')[0]
        
    def writeWithTemplate(self, values, html_file_name):
        values["version"] = self.getVersion() 
        values["version_datetime"] = self.getTimeStampString()
        if get_current_user() is None:
            values["googleLoginUrl"] = create_login_url()
        else:
            values["googleLogoutUrl"] = create_logout_url("/OdenkiUser")
        self.response.out.write(template.render("html/" + html_file_name + ".html", values))
        
    def writePage(self, title=None, script="", body=""):
        if title is None:
            title = getMainModuleName()
        assert isinstance(title, str)
        assert isinstance(script, str)
        assert isinstance(body, str)
        v = {}
        v["title"] = title
        v["script"] = script
        v["body"] = body
        v["version"] = self.getVersion()
        v["version_datetime"] = self.getTimeStampString()
        self.response.out.write(template.render("html/MyRequestHandler.html", v))
        
    def doesAcceptJson(self):
        matched = self.request.accept.best_match(["application/json", "application/json-rpc"])
        return True if matched else False
        
    def doesAcceptText(self):
        matched = self.request.accept.best_match(["text/*"])
        return True if matched else False
        
    def writeJson(self):
        if self.doesAcceptJson():
            self.response.content_type = "application/json"
        else:
            self.response.content_type = "text/json"
        self.response.out.write(dumps(self.jsonResponse))
        
    def writeJsonRpc(self):
        if getattr(self, "jsonResponse", None) is None:
            self.jsonResponse = {}
            if self.jsonRequest.get("method") == "echo":
                self.jsonResponse = self.jsonRequest
        if self.jsonResponse.get("id") is None:
            assert isinstance(self.jsonRequest, dict)
            self.jsonResponse["id"] = self.jsonRequest.get("id")            
        self.writeJson()
        
    def getJsonFromUrl(self):
        json_from_url = {}
        for k, v in self.request.params.items():
            if json_from_url.get(k):
                if isinstance(json_from_url[k], list):
                    json_from_url[k].append(v)
                else:
                    json_from_url[k] = [json_from_url[k], v]
            else:
                json_from_url[k] = v
        
        base64_params = json_from_url.get("params")
        if base64_params:
            params = base64_decode(base64_params)
        else:
            params = "[]"
        json_from_url["params"] = loads(params)
        return json_from_url
            
    def getJsonFromBody(self):
        json_from_body = loads(self.request.body)
        if json_from_body is None:
            json_from_body = {}
        assert isinstance(json_from_body, dict)
        return json_from_body

    def getJsonRequest(self):
        if self.request.method == "POST" or self.request.method == "PUT":
            # POST can change the state of servers.
            # PUT should be idempotent.
            debug("POST or PUT")
            try:
                self.jsonRequest = self.getJsonFromBody()
                assert isinstance(self.jsonRequest, dict)
                return self.jsonRequest
            except JSONDecodeError, e:
                debug("JSONDecodeError, " + self.request.body)
                self.jsonRequest = None
                self.setJsonRpc2ErrorResponse(JSON_RPC_ERROR_PARSE_ERROR, e.message)
                return None  
        elif self.request.method == "GET" or self.request.method == "DELETE":
            debug("GET or DELETE")
            # GET should not change the state of servers.
            # DELETE should be idempotent.
            try:
                self.jsonRequest = self.getJsonFromUrl()
                assert isinstance(self.jsonRequest, dict)
                return self.jsonRequest
            except JSONDecodeError, e:
                debug("JSONDecodeError, " + self.request.url)
                self.jsonRequest = None
                self.setJsonRpc2ErrorResponse(JSON_RPC_ERROR_PARSE_ERROR, e.message)
                return None  
        else:
            self.jsonRequest = None
            self.setJsonRpc2ErrorResponse(JSON_RPC_ERROR_INVALID_REQUEST,
                                          "%s is unknown HTTP method" % self.request.method)
            return None
        assert self.jsonRequest is not None
    
    def setJsonResponse(self, dictionary):
        assert isinstance(dictionary, dict)
        self.jsonResponse = dictionary
    
    def setJsonRpc2ErrorResponse(self, code, message, data=None, extra=None):
        assert isinstance(code, int)
        assert isinstance(message, str)
        if getattr(self, "jsonResponse", None) is None:
            self.jsonResponse = {}
        if extra is not None:
            assert isinstance(extra, dict)
            self.jsonResponse.update(extra)
        self.jsonResponse["code"] = code
        self.response.set_status(toHttpStatus(code))
        self.jsonResponse["message"] = message
        self.jsonResponse["jsonrpc"] = "2.0"
        
    def setJsonRpc2SuccessResponse(self, result=None, extra=None):
        if getattr(self, "jsonResponse", None) is None:
            self.jsonResponse = {}
        if extra is not None:
            assert isinstance(extra, dict)
            self.jsonResponse.update(extra)
        self.jsonResponse["result"] = result
        self.jsonResponse["jsonrpc"] = "2.0"

class _RequestHandler(MyRequestHandler):
    
    def get(self):
        debug("MyRequestHandler get")
        if self.request.params.items().__len__() == 0:
            self.testPage()
            return
        debug("_RequestHandler.get was called.")
        self.getJsonRequest()
        assert isinstance(self.jsonRequest, dict)
        self.writeJsonRpc()
        pass
    
    def post(self):
        debug("MyRequestHandler post")
        self.getJsonRequest()
        assert isinstance(self.jsonRequest, dict) or isinstance(self.jsonRequest, list) or self.jsonRequest is None
        self.writeJsonRpc()
    
    def testPage(self):
        html = """
<p>MyRequestHandler is customized version of RequestHandler that implements
some methods to handle JSON-RPC 2.0 over HTTP.</p>
<table border="1px">
<tr><th>request</th><th>response</th></tr>
<tr><td id="request1"/>request1</td><td id="response1">response1</td></tr>
<tr><td id="request2"/>request2</td><td id="response2">response2</td></tr>
<tr><td id="request3"/>request3</td><td id="response3">response3</td></tr>
<tr><td id="request4"/>request4</td><td id="response4">response4</td></tr>
</table>"""
        script = """
    var url = "?id=123&x=1&x=2&method=echo";
    $.ajax({
        datatype: "json",
        url: url,
        type: "GET",
        success: function(j){
            $("#request1").text(url);
            $("#response1").text(j);
        }
    });
    var data2 = '{id:3, method:"echo"}';
    $.ajax({
        datatype: "json",
        url: "MyRequestHandler",
        type: "POST",
        data: data2,
        success: function(j){
            $("#request2").text(data2);
            $("#response2").text(j);
        },
        error: function(j, text_status, error_thrown){
            $("#request2").text(data2);
            $("#response2").text(error_thrown);
        }
    });
    var data3 = '{"id":3, "method":"echo"}';
    $.ajax({
        datatype: "json",
        url: "MyRequestHandler",
        type: "POST",
        data: data3,
        success: function(j){
            $("#request3").text(data3);
            $("#response3").text(j);
        },
        error: function(j, text_status, error_thrown){
            $("#request3").text(data3);
            $("#response3").text(error_thrown);
        }
    });
    var data4 = "{'id':3, 'method':'echo'}";
    $.ajax({
        datatype: "json",
        url: "MyRequestHandler",
        type: "POST",
        data: data4,
        success: function(j){
            $("#request4").text(data4);
            $("#response4").text(j);
        },
        error: function(j, text_status, error_thrown){
            $("#request4").text(data4);
            $("#response4").text(error_thrown);
        }
    });
        """
        self.writePage("MyRequestHandler", script, html)

def main():
    debug("MyRequestHandler main")
    from google.appengine.ext.webapp import WSGIApplication
    from google.appengine.ext.webapp.util import run_wsgi_app
    application = WSGIApplication([('/' + getMainModuleName(),
                                    getMainModuleRequestHandler())], debug=True)
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()
