import datetime 
import dateutil.parser
import lib
#from lib import debug

_ANCIENT = "Fri, 01 Jan 1990 00:00:00 GMT"

class _GMT(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=0)
    def dst(self, dt):
        return datetime.timedelta(0)
    def tzname(self, dt):
        return "GMT"

def getNow():
    dt = datetime.datetime.now()
    assert isinstance(dt, datetime.datetime)
    dt = dt.replace(tzinfo=_GMT())
    rfc_format = toRfcFormat(dt)
    dt = fromRfcFormat(rfc_format)
    return dt

def getIfModifiedSince(request):
    from google.appengine.ext.webapp import Request
    assert isinstance(request, Request)
    rfc_format = request.headers.get("If-Modified-Since", None)
    return fromRfcFormat(rfc_format)

def fromRfcFormat(rfc_format):
    if rfc_format is None:
        dt = dateutil.parser.parse(_ANCIENT)
        assert isinstance(dt, datetime.datetime)
        assert dt.tzinfo is not None
        return dt 
    else:
        assert isinstance(rfc_format, str)
        dt = dateutil.parser.parse(rfc_format)
        assert isinstance(dt, datetime.datetime)
        assert dt.tzinfo is not None
        return dt

def toRfcFormat(dt):
    if dt is None:
        return _ANCIENT
    assert isinstance(dt, datetime.datetime)
    assert dt.tzinfo is not None
    return dt.strftime("%a, %d %b %Y %H:%M:%S %Z")

if __name__ == "__main__":
    before = getNow()
    rfc_format = toRfcFormat(before)
    after = fromRfcFormat(rfc_format)
    assert before == after
    lib.debug("test finished")
