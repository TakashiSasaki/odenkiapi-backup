from __future__ import unicode_literals, print_function
#from google.appengine import runtime
from model.NdbModel import NdbModel
from model.Columns import Columns
#from model.Columns import Columns
#from model.Command import getCommandById
#__all__ = ["JsonRpcError", "JsonRpcRequest", "JsonRpcResponse", "JsonRpcDispatcher"]
import logging as _logging
from lib.json.JsonRpcError import JsonRpcException
import gaesessions
_logging.getLogger().setLevel(_logging.DEBUG)
#from exceptions import Exception
#from lib.JsonEncoder import dumps
from google.appengine.ext.webapp import RequestHandler, Response
from StringIO import StringIO
import csv
from logging import debug, error, info
from warnings import warn
from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError, dumps
#from lib.json import dumps

class JsonRpcDispatcher(RequestHandler):
    """JsonRpcDispatcher invokes corresponding methods according to given method parameter"""
    __slot__ = ["methodList", "jsonRpc"]
    
    def __init__(self, request, response):
        RequestHandler.__init__(self, request, response)
        self._initMethodList()

    def _initMethodList(self):
        """ It registers user methods to self.methodList.
        User methods are expected to take just one JSON-RPC object.  
        """
        self.methodList = {}
        self.methodList.update(self.__class__.__dict__)
        assert isinstance(self.methodList, dict)
        
        def d(key):
            try:
                del self.methodList[key]
            except KeyError:
                pass

        d("__slot__")
        d("__module__")
        d("__main__")
        d("__dict__")
        d("__weakref__")
        d("__doc__")
        d("__init__")
        d("get")
        d("post")
        d("put")
        d("head")
        d("options")
        d("delete")
        d("trace")
        d("_write")
        d("_invokeMethod")
        d("_initMethodList")
        
        for k, v in self.methodList.iteritems():
            if isinstance(k, str):
                self.methodList[k.decode()] = v
    
    def _invokeMethod(self, method_name, json_rpc_request):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        json_rpc_response = JsonRpcResponse(json_rpc_request.getId())
        try:
            x = self.methodList[method_name](self, json_rpc_request, json_rpc_response)
            if x: warn("dispatched method need not return an object of JsonRpcResponse.")
        except JsonRpcException, e:
            from sys import exc_info
            (etype, value, tb) = exc_info()
            from traceback import print_exception
            print_exception(etype, value, tb)
            json_rpc_response.setError(e.code, e.message, e.data)

        # cancel redirection for debug purpose
        if json_rpc_request.getValue("debug"):
            if json_rpc_response.getRedirectTarget():
                json_rpc_response.setResultValue("cancelled_redirect_target_for_debug", json_rpc_response.getRedirectTarget())
                del(json_rpc_response._redirectTarget)

        return json_rpc_response
    
    def get(self, *args):
        jrequest = JsonRpcRequest(self.request)
        jresponse = self._invokeMethod(jrequest.method, jrequest)
        self._write(jresponse)

    def post(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)
    
    def put(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)
    
    def head(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)
    
    def options(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)
        
    def delete(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)
        
    def trace(self, *args):
        json_rpc_request = JsonRpcRequest(self.request)
        json_rpc_response = self._invokeMethod(json_rpc_request.method, json_rpc_request)
        self._write(json_rpc_response)

    def _write(self, json_rpc_response):
        """write JSON-RPC response as it is"""
        assert isinstance(json_rpc_response, JsonRpcResponse)
        assert isinstance(json_rpc_response, dict)

        if json_rpc_response.getRedirectTarget():
            assert isinstance(self.response, Response)
            self.redirect(json_rpc_response.getRedirectTarget())
            debug("redirecting to %s" % json_rpc_response.getRedirectTarget())
            return
        
        # notification has no id
        if json_rpc_response.getId() is None:
            debug("JSON-RPC notification")
            if not json_rpc_response.has_key("error") and not json_rpc_response.has_key("result"):
                # http://www.simple-is-better.org/json-rpc/jsonrpc20-over-http.html
                self.response.set_status(204) # No content
                self.response.content_type = "text/plain"
                return
            json_rpc_response.setError(JsonRpcError.INVALID_REQUEST, "Response for notification should have neither result nor error.")

        if json_rpc_response.has_key("error"):
            debug("JSON RPC response with error.")
            assert  json_rpc_response.getResult() is None
            self.response.content_type = "application/json"
            self.response.status = JsonRpcDispatcher._getHttpStatusFromJsonRpcError(json_rpc_response.getErrorCode()) 
            self.response.out.write(dumps(json_rpc_response))
            return
        
        # HTTP response in given format
        if self.request.get("format") == "tsv":
            self._writeTsv(json_rpc_response)
            return
        if self.request.get("format") == "csv":
            self._writeCsv(json_rpc_response)
            return
        if self.request.get("format") == "DataTable":
            self._writeDataTable(json_rpc_response)
            return
        self._writeJson(json_rpc_response)
    
    def _writeJson(self, json_rpc_response):
        assert isinstance(json_rpc_response, JsonRpcResponse)
        assert isinstance(json_rpc_response, dict)
        self.response.content_type = "application/json"
        json_string = dumps(json_rpc_response)
        callback = self.request.get("callback")
        if callback:
            self.response.out.write("%s=(%s)" %(callback, json_string))
            return
        self.response.out.write(dumps(json_rpc_response))
        return

#    def _writeJsonP(self, json_rpc_response):
#        result = json_rpc_response.getResult()
#        if not isinstance(result, dict) or not isinstance(result, list):
#            raise RuntimeError("result is neither dict or list")
#        self.response.out.write(dumps(result))
#        self.response.content_type = "application/javascript"
    
    def _writeCsv(self, json_rpc_response, dialect=csv.excel, content_type="text/csv"):
        assert isinstance(json_rpc_response, JsonRpcResponse)
        output = StringIO()
        csv_writer = csv.writer(output, dialect)
        columns = json_rpc_response.getColumns()
        if not columns:
            warn("Column description is not set in JSON-RPC response object.") 
            return
        assert isinstance(columns, Columns)
        csv_writer.writerow(columns.getColumnIds())
        result = json_rpc_response.getResult()
        if not isinstance(result, list): 
            warn("Result must be a list to emit CSV.") 
            return
        for record in result:
            if isinstance(record, NdbModel):
                csv_writer.writerow(record.to_list(columns))
                continue
            if isinstance(record, list):
                csv_writer.writerow(record)
                continue
            error("result contains neither list nor NdbModel")
        self.response.out.write(output.getvalue())
        self.response.content_type = content_type
    
    def _writeTsv(self, json_rpc_response):
        self._writeCsv(json_rpc_response, dialect=csv.excel_tab, content_type="application/vnd.ms-excel")        
        
    def _writeDataTable(self, jresponse):
        debug("format=DataTable")
        assert isinstance(jresponse, JsonRpcResponse)
        columns = jresponse.getColumns()
        if not columns:
            warn("Column description is not set in JSON-RPC response object.") 
            return
        assert isinstance(columns, Columns)
        rows = []
        for x in jresponse.getResult():
            assert isinstance(x, NdbModel)
            row = x.to_row(columns)
            debug(row)
            rows.append(row)
        data_table = {"cols": jresponse.getColumns(), "rows":rows}
        info(str(data_table))
        self.response.out.write(dumps(data_table))
        self.response.content_type = "application/javascript"

    @classmethod
    def _getHttpStatusFromJsonRpcError(cls, json_rpc_error):
        if json_rpc_error == JsonRpcError.PARSE_ERROR:
            return 500
        if json_rpc_error == JsonRpcError.INVALID_REQUEST:
            return 400
        if json_rpc_error == JsonRpcError.METHOD_NOT_FOUND:
            return 404
        if json_rpc_error == JsonRpcError.INVALID_PARAMS:
            return 500
        if json_rpc_error == JsonRpcError.INTERNAL_ERROR:
            return 500
        if json_rpc_error >= JsonRpcError.SERVER_ERROR_RESERVED_MIN and json_rpc_error <= JsonRpcError.SERVER_ERROR_RESERVED_MAX:
            return 500
        return None
    
    def doesAcceptHtml(self, jrequest, jresponse):
        if self.request.accept.accept_html(): return True
        self.response.setHttpStatus(406)
        assert isinstance(jresponse, JsonRpcResponse)
        error_message = "user agent does not accept text/html response"
        jresponse.setError(JsonRpcError.INVALID_REQUEST, error_message)
