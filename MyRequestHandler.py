from os import environ
environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
CACHE_BACKEND = 'memcached:///'

from lib.BasicPage import BasicPage
class MyRequestHandler(BasicPage):
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
    
if __name__ == "__main__":
    from lib import runWsgiApp
    runWsgiApp(MyRequestHandler, "/MyRequestHandler")
    
