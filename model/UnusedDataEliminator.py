from __future__ import unicode_literals, print_function
from logging import info
from model.DataNdb import Data
from model.MetadataNdb import Metadata
from google.appengine.ext.deferred import defer
from google.appengine.runtime import DeadlineExceededError

class UnusedDataEliminator(object):
    __slots__ = ["currentDataId", "end", "nDeleted"]
    
    def __init__(self, start, end):
        self.currentDataId = start
        self.end = end
        self.nDeleted = 0
        
    def run(self):
        info("deleting unused Data entity between %s and %s" % (self.currentDataId, self.end))
        try:
            self.eliminateUnusedData()
            info("%s Data entities were deleted" % self.nDeleted)
        except DeadlineExceededError:
            info("%s Data entities were deleted and continues" % self.nDeleted)
            defer(self.run)
        
    #@ndb.toplevel
    def eliminateUnusedData(self):
        query = Data.queryRange(self.currentDataId, self.end)
        for data_key in query.iter(keys_only=True):
            data = data_key.get()
            if data: self.currentDataId = data_key.get().dataId
            metadata_query = Metadata.queryByData(data_key)
            metadata_key = metadata_query.get(keys_only=True)
            if metadata_key: continue
            #info("deleting data_key=%s (data_id = %s)" % (data_key, data_key.get().dataId))
            self.nDeleted += 1
            data_key.delete()
