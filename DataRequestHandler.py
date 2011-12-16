import logging
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
from google.appengine.ext.webapp import  template
from django.utils import  simplejson as json
#import json
from Data import Data
from google.appengine.ext import db

class DataRequestHandler(webapp.RequestHandler):
    
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
        
        self.response.out.write(template.render("html/Data.html", template_values))


application = webapp.WSGIApplication([('/Data', DataRequestHandler)], debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
