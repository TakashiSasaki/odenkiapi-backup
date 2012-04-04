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

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/RawData', RawDataRequestHandler)], debug=True)
    run_wsgi_app(application)
