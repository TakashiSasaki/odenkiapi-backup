import logging
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
from google.appengine.ext.webapp import  template
from django.utils import  simplejson as json
#import json
from RawData import RawData
from MyRequestHandler import MyRequestHandler
import simplejson

class RawDataRequestHandler(MyRequestHandler):
    
    def get(self):
        template_values = {}
        template_values["all_raw_data"] = []
        gql = RawData.gql("ORDER BY rawDataId DESC LIMIT 100")
        all_raw_data = gql.run()
        #all_raw_data = RawData.all()
        for raw_data in all_raw_data:
            raw_data_dict = {"rawDataId": raw_data.rawDataId,
                            "path":raw_data.path,
                            "parameters": raw_data.parameters,
                            "query": raw_data.query,
                            "fragment":raw_data.fragment,
                            "body": raw_data.body }
            logging.info(raw_data_dict)
            template_values["all_raw_data"].append(raw_data_dict)
        
        self.writeWithTemplate(template_values, "RawData")
        
class RawDataRequestHandler2(MyRequestHandler):
    def get(self):
        gql = RawData.gql("ORDER BY rawDataId DESC LIMIT 5000")
        records = gql.run()
        results = []
        for record in records:
            query_dict = cgi.parse_qs(record.query)
            if query_dict.has_key("arduinoid"):
                gen_power = query_dict["gen.power(W)"][0]
                timestring = query_dict["time"][0]
                results.append([gen_power, timestring[0:4], timestring[4:6], timestring[6:8], timestring[8:10], timestring[10:12], timestring[12:14]])
                #results.append([gen_power])
        self.response.out.write(self.request.get("callback") + "(" +  simplejson.dumps({"timeVsWatt":results}) + ");")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/RawData', RawDataRequestHandler), ('/RawData2', RawDataRequestHandler2)], debug=True)
    run_wsgi_app(application)
