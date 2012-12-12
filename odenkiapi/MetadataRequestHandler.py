import logging
from model.Metadata import Metadata, getDataIds
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
    from lib.gae import run_wsgi_app
    run_wsgi_app([('/Metadata', MetadataRequestHandler)])
