import logging
from urlparse import urlparse
from google.appengine.ext import db
from google.appengine.ext.webapp import Request
from Counter import Counter

class RawData(db.Model):
    rawDataId = db.IntegerProperty()
    path = db.StringProperty()
    parameters = db.StringProperty()
    query = db.StringProperty()
    fragment = db.StringProperty()
    body = db.StringProperty()
    
def GetRawData(request):
    logging.info(("GetRawData", request.url))
    assert isinstance(request, Request)
    parsed_url = urlparse(request.url)
    logging.info(parsed_url)
    path = parsed_url.path
    parameters = parsed_url.params
    query = parsed_url.query
    fragment = parsed_url.fragment
    body = request.body
    gql_query = RawData.gql("WHERE path = :1 AND parameters = :2 AND query= :3 AND fragment = :4 AND body = :5", path, parameters, query, fragment, body)
    existing_raw_data = gql_query.get()
    logging.info(existing_raw_data)
    logging.info((path, parameters, query, fragment, body))
    if existing_raw_data is not None:
        return existing_raw_data
    else:
        raw_data = RawData()
        raw_data.rawDataId = Counter.GetNextId("rawDataId")
        raw_data.path = path
        raw_data.parameters = parameters
        raw_data.query = query
        raw_data.fragment = fragment
        raw_data.body = body
        return raw_data.put()
