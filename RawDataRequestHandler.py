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
from google.appengine.ext.db import Query, GqlQuery
from google.appengine.ext.webapp import RequestHandler
from google.appengine.api import memcache
from google.appengine.api.datastore import typename, Key

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
            #logging.info(raw_data_dict)
            template_values["all_raw_data"].append(raw_data_dict)
        
        self.writeWithTemplate(template_values, "RawData")
        
class RawDataCached(MyRequestHandler):
    def get(self):
        client = memcache.Client()
        LIMIT = 100

        if len(self.request.get("clear")) != 0:
            client.delete("key_list")
            
        template_values = {}
        template_values["all_raw_data"] = []

        
        old_key_list = client.get("key_list")
        if old_key_list is None:
            old_key_list = []
            query = Query(RawData, keys_only=True)
            query.order("-rawDataId")
            new_key_list = []
            count = 0
            for key_in_query in query:
                count += 1
                if count >= LIMIT: break
                if key_in_query in old_key_list: break
                new_key_list.append(key_in_query)
            
            all_key_list = new_key_list + old_key_list
            all_key_list = all_key_list[:LIMIT]
            client.set("key_list", all_key_list, 15)
        else:
            all_key_list = old_key_list

        for key_in_list in all_key_list:
            raw_data = client.get(str(key_in_list))
            if not isinstance(raw_data, RawData):
                raw_data_list = RawData.get([key_in_list])
                if len(raw_data_list) != 1: continue
                raw_data = raw_data_list[0]
                if not isinstance(raw_data, RawData): continue
                client.set(str(key_in_list), raw_data)
            if not isinstance(raw_data, RawData): continue

            raw_data_dict = {"rawDataId": raw_data.rawDataId,
                            "path":raw_data.path,
                            "parameters": raw_data.parameters,
                            "query": raw_data.query,
                            "fragment":raw_data.fragment,
                            "body": raw_data.body }
            #logging.info(raw_data_dict)
            template_values["all_raw_data"].append(raw_data_dict)
        
        self.writeWithTemplate(template_values, "RawData")

class RawDataRequestHandler2(MyRequestHandler):
    def get(self):
        client = memcache.Client()
        LIMIT = 5000
        
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
        self.response.out.write(self.request.get("callback") + "(" + simplejson.dumps({"timeVsWatt":results}) + ");")

class RawData2Cached(MyRequestHandler):
    def get(self):
        client = memcache.Client()
        LIMIT = 3000
        
        gql_query = GqlQuery("SELECT __key__ FROM RawData ORDER BY rawDataId DESC LIMIT 5000")
        #query = Query(RawData, keys_only=True)
        #query.order("-rawDataId")

        results = []
        hit_count = 0
        read_count = 0
        for key in gql_query.run(limit=LIMIT, keys_only=True):
            query_dict = client.get(str(key), namespace="RawData2Cached")
            #if query_dict is None:
            if True:
                #records = RawData.get([key])
                #record = records[0]
                #if not isinstance(record, RawData): continue
                #query_dict = cgi.parse_qs(record.query)
                #client.set(str(key), query_dict, namespace="RawData2Cached")
                read_count += 1
            else:
                hit_count += 1
            
            #if query_dict.has_key("arduinoid"):
            #    gen_power = query_dict["gen.power(W)"][0]
            #    timestring = query_dict["time"][0]
            #    results.append([gen_power, timestring[0:4], timestring[4:6], timestring[6:8], timestring[8:10], timestring[10:12], timestring[12:14]])
                #results.append([gen_power])
        
        logging.info("hit_count = %s, read_count = %s" % (hit_count, read_count))
        self.response.out.write(self.request.get("callback") + "(" + simplejson.dumps({"timeVsWatt":results}) + ");")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/RawData', RawDataCached), ('/RawData2', RawDataRequestHandler2), ('/RawDataNonCached', RawDataRequestHandler)
                                          , ('/RawData2Cached', RawData2Cached)
                                          ], debug=True)
    run_wsgi_app(application)
