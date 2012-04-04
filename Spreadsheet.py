from MyRequestHandler import MyRequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication
from GoogleDocs import getSpreadsheetsClient, getDocsClient, loadAccessToken
from gdata.docs.data import Resource
from gdata.spreadsheets.data import Spreadsheet, WorksheetsFeed, \
    SpreadsheetsFeed, WorksheetEntry
from gdata.spreadsheets.client import SpreadsheetsClient
from OdenkiUser import getCurrentUser, OdenkiUser
from logging import debug, getLogger, DEBUG
from gdata.client import RequestError, Unauthorized
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
        client = getDocsClient()
        try:
            debug("trying to get existing collection by id = " + odenki_user.docsCollectionId)
            existing_collection = client.GetResourceById(odenki_user.docsCollectionId)
            debug("succeeded to get existing collection")
            assert isinstance(existing_collection, Resource)
            return existing_collection
        except RequestError, e :
            odenki_user.docsCollectionId = None
            odenki_user.put()
        except DownloadError, e:
            odenki_user.docsCollectionId = None
            odenki_user.put()

    client = getDocsClient()
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
        client = getDocsClient()
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

    client = getDocsClient()
    new_spreadsheet = Resource(type="spreadsheet", title=ODENKI_SPREADSHEET_NAME)
    created_spreadsheet = client.CreateResource(new_spreadsheet, collection=getOdenkiFolder())
    assert isinstance(created_spreadsheet, Resource)
    odenki_user.docsSpreadsheetId = created_spreadsheet.resource_id.text
    odenki_user.put()
    return created_spreadsheet

def getOdenkiSpreadsheetKey():
    spreadsheet_resource = getOdenkiSpreadsheet()
    spreadsheet_key = spreadsheet_resource.resource_id.text.split(":")[1]
    return spreadsheet_key

def getWorksheet(worksheet_id):
    spreadsheets_client = getSpreadsheetsClient()
    spreadsheet_key = getOdenkiSpreadsheetKey()
    debug("trying to get existing worksheet by worksheet_id = " + worksheet_id)
    worksheet = spreadsheets_client.GetWorksheet(spreadsheet_key, worksheet_id)
    if worksheet is not None:
        debug("Succeeded to get existing worksheet " + worksheet.GetId())
        assert isinstance(worksheet, WorksheetEntry)
        return worksheet

def createWorksheet(title, rows, cols):
    spreadsheets_client = getSpreadsheetsClient()
    spreadsheet_key = getOdenkiSpreadsheetKey()
    new_worksheet = spreadsheets_client.add_worksheet(spreadsheet_key=spreadsheet_key, title=title, rows=rows, cols=cols)
    assert isinstance(new_worksheet, WorksheetEntry)
    return new_worksheet

def getCommandWorksheet():
    odenki_user = getCurrentUser()
    assert isinstance(odenki_user, OdenkiUser)
    if odenki_user.docsCommandWorksheetId is not None:
        try :
            worksheet = getWorksheet(odenki_user.docsCommandWorksheetId)
            assert isinstance(worksheet, WorksheetEntry)
            return worksheet
        except RequestError, e:
            debug("failed to get worksheet " + odenki_user.docsCommandWorksheetId)
            odenki_user.docsCommandWorksheetId = None
            odenki_user.put()            

    worksheet = createWorksheet("command", 100, 7)
    assert isinstance(worksheet, WorksheetEntry)
    odenki_user.docsCommandWorksheetId = worksheet.get_worksheet_id()
    odenki_user.put()
    return worksheet

def getWorksheetGid(worksheet_id):
    spreadsheets_client = getSpreadsheetsClient()
    spreadsheet_key = getOdenkiSpreadsheetKey()
    worksheets = spreadsheets_client.GetWorksheets(spreadsheet_key)
    assert isinstance(worksheets, WorksheetsFeed)
    count = 0
    for x in worksheets.entry:
        assert isinstance(x, WorksheetEntry)
        if x.GetWorksheetId() == worksheet_id:
            return count
        count += 1
    return None
    

class _RequestHandler(MyRequestHandler):
    def get(self):
        folder = getOdenkiFolder()
        assert isinstance(folder, Resource)
        spreadsheet = getOdenkiSpreadsheet()
        assert isinstance(spreadsheet, Resource) 
        command_worksheet = getCommandWorksheet()
        assert isinstance(command_worksheet, WorksheetEntry)
        v = {}
        v["folder_title"] = folder.title
        v["folder_id"] = folder.resource_id
        v["folder_link"] = folder.find_html_link()
        v["spreadsheet_title"] = spreadsheet.title
        v["spreadsheet_id"] = spreadsheet.resource_id
        v["spreadsheet_link"] = spreadsheet.find_html_link()
        v["command_worksheet_link"] = spreadsheet.find_html_link() + "#gid=" + str(getWorksheetGid(command_worksheet.GetWorksheetId())) 
        self.writeWithTemplate(v, "Spreadsheet")

if __name__ == "__main__":
    application = WSGIApplication([('/Spreadsheet', _RequestHandler)], debug=True)
    run_wsgi_app(application)
