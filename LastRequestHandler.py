'''
Created on 2012/03/14

@author: sasaki
'''

import logging
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
from google.appengine.ext.webapp import  template
from django.utils import  simplejson as json
from Sender import Sender
from Counter import Counter
from Metadata import Metadata
from google.appengine.ext import db
from google.appengine.ext.db import Key
from Data import Data

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class LastRequestHandler(webapp.RequestHandler):
    
    def get(self):
        gql_query = Metadata.gql("ORDER BY receivedDateTime DESC");
        metadata_list = gql_query.fetch(10)
        
        for metadata in metadata_list:
            assert isinstance(metadata, Metadata)
            assert isinstance(metadata.sender, Sender)
        
            all_data = {}
            all_data_string = ""
            for data_key in metadata.dataList:
                assert isinstance(data_key, Key)
                data = Data.get(data_key)
                assert isinstance(data, Data)
                logger.debug(data.field)
                logger.debug(data.string)
                all_data_string = all_data_string + data.field + " = " + data.string + "<br/>"
                all_data[data.field] = data.string
            if all_data.has_key("longitude") and all_data.has_key("latitude"):
                break

        all_data_string = "received at " + str(metadata.receivedDateTime) + "<br/>" + all_data_string
        template_values = {"longitude": all_data["longitude"], "latitude": all_data["latitude"], "all_data":all_data, "all_data_string": all_data_string}
        logging.debug(str(template_values))        
        self.response.out.write(template.render("html/Last.html", template_values))

application = webapp.WSGIApplication([('/Last', LastRequestHandler)], debug=True)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
