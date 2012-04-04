import logging
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
from django.utils import  simplejson as json
#import json
from Metadata import Metadata, getDataIds
from google.appengine.ext import db
from MyRequestHandler import MyRequestHandler

class MetadataRequestHandler(MyRequestHandler):
    
    def get(self):
        template_values = {}
        template_values["all_metadata"] = []
        gql = Metadata.gql("ORDER BY metadataId DESC LIMIT 100")
        recent = gql.run()
        #all_raw_data = RawData.all()
        logging.info(recent)
        for metadata in recent:

            logging.info(type(metadata.receivedDateTime)) 
            metadata_dict = {"metadataId": metadata.metadataId,
                            "receivedDateTime":metadata.receivedDateTime,
                            "sender": metadata.sender.senderId,
                            "rawData": metadata.rawData.rawDataId,
                            "dataList": getDataIds(metadata) }
            logging.info(metadata_dict)
            template_values["all_metadata"].append(metadata_dict)
        
        self.writeWithTemplate(template_values, "Metadata")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/Metadata', MetadataRequestHandler)], debug=True)
    run_wsgi_app(application)
