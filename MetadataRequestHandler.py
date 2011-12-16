import logging
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
from google.appengine.ext.webapp import  template
from django.utils import  simplejson as json
#import json
from Metadata import Metadata
from google.appengine.ext import db

class MetadataRequestHandler(webapp.RequestHandler):
    
    def get(self):
        template_values = {}
        template_values["all_metadata"] = []
        gql = Metadata.gql("ORDER BY metadataId DESC LIMIT 100")
        recent = gql.run()
        #all_raw_data = RawData.all()
        logging.info(recent)
        for metadata in recent:
            data_list = []
            for key in metadata.dataList:
                data = db.get(key)
                data_list.append(data.dataId)
            logging.info(type(metadata.receivedDateTime)) 
            metadata_dict = {"metadataId": metadata.metadataId,
                            "receivedDateTime":metadata.receivedDateTime,
                            "sender": metadata.sender.senderId,
                            "rawData": metadata.rawData.rawDataId,
                            "dataList": data_list }
            logging.info(metadata_dict)
            template_values["all_metadata"].append(metadata_dict)
        
        self.response.out.write(template.render("html/Metadata.html", template_values))


application = webapp.WSGIApplication([('/Metadata', MetadataRequestHandler)], debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
