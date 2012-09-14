import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
#import json
from model.Data import Data
from MyRequestHandler import MyRequestHandler

class DataRequestHandler(MyRequestHandler):
    
    def get(self):
        template_values = {}
        template_values["all_data"] = []
        gql = Data.gql("ORDER BY dataId DESC LIMIT 100")
        recent = gql.run()
        #all_raw_data = RawData.all()
        logging.info(recent)
        for data in recent:
            data_dict = {"dataId": data.dataId,
                            "field": data.field,
                            "string": data.string }
            logging.info(data_dict)
            template_values["all_data"].append(data_dict)
        
        self.writeWithTemplate(template_values, "Data")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/Data', DataRequestHandler)], debug=True)
    run_wsgi_app(application)
