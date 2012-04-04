from MyRequestHandler import MyRequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication
from GoogleDocs import getClient
from gdata.docs.data import Resource
from OdenkiUser import getCurrentUser, OdenkiUser
from logging import debug, getLogger, DEBUG
from gdata.client import RequestError
from google.appengine.api.urlfetch import DownloadError
getLogger().setLevel(DEBUG)

ODENKI_FOLDER_NAME = "Odenki"
ODENKI_SPREADSHEET_NAME = "Odenki"

def getOdenkiFolder():
    odenki_user = getCurrentUser()
    assert isinstance(odenki_user, OdenkiUser)
    
    debug("odenki user = " + odenki_user.odenkiNickname)
    if odenki_user.docsCollectionId is not None:
        debug("docsCollectionId : " + odenki_user.docsCollectionId)
        client= getClient()
        try:
            debug("trying to get existing collection by id = " + odenki_user.docsCollectionId)
            existing_collection = client.GetResourceById(odenki_user.docsCollectionId)
            debug("succeeded to get existing collection")
            assert isinstance(existing_collection, Resource)
            return existing_collection
        except RequestError,e :
            odenki_user.docsCollectionId = None
            odenki_user.put()
        except DownloadError, e:
            odenki_user.docsCollectionId = None
            odenki_user.put()

    client = getClient()
    new_collection = Resource(type="folder", title=ODENKI_FOLDER_NAME)
    created_collection = client.CreateResource(new_collection)
    assert isinstance(created_collection, Resource)
    odenki_user.docsCollectionId = created_collection.resource_id.text
    odenki_user.put()
    return created_collection

def getOdenkiSpreadsheet():
    odenki_user = getCurrentUser()
    assert isinstance(odenki_user, OdenkiUser)
    
    if odenki_user.docsSpreadsheetId is not None:
        client= getClient()
        try:
            existing_spreadsheet = client.GetResourceById(odenki_user.docsSpreadsheetId)
            assert isinstance(existing_spreadsheet, Resource)
            return existing_spreadsheet
        except RequestError, e:
            odenki_user.docsSpreadsheetId = None
            odenki_user.put()
        except DownloadError, e:
            odenki_user.docsSpreadsheetId = None
            odenki_user.put()

    client = getClient()
    new_spreadsheet = Resource(type="spreadsheet", title=ODENKI_SPREADSHEET_NAME)
    created_spreadsheet = client.CreateResource(new_spreadsheet, collection=getOdenkiFolder())
    assert isinstance(created_spreadsheet, Resource)
    odenki_user.docsSpreadsheetId = created_spreadsheet.resource_id.text
    odenki_user.put()
    return created_spreadsheet

class _RequestHandler(MyRequestHandler):
    def get(self):
        folder = getOdenkiFolder()
        assert isinstance(folder, Resource)
        spreadsheet = getOdenkiSpreadsheet()
        assert isinstance(spreadsheet, Resource) 
        v = {}
        v["folder_title"] = folder.title
        v["folder_id"] = folder.resource_id
        v["folder_link"] = folder.find_html_link()
        v["spreadsheet_title"] = spreadsheet.title
        v["spreadsheet_id"] = spreadsheet.resource_id
        v["spreadsheet_link"] = spreadsheet.find_html_link()
        self.writeWithTemplate(v, "Spreadsheet")

if __name__ == "__main__":
    application = WSGIApplication([('/Spreadsheet', _RequestHandler)], debug=True)
    run_wsgi_app(application)
