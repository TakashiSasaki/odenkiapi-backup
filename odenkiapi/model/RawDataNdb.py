# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from google.appengine.ext import ndb
# from google.appengine.ext.webapp import Request
# from model.Counter import Counter
# from json import dumps
from logging import debug
# from model.NdbModel import NdbModel
from model.Columns import Columns
from model.CsvMixin import CsvMixin
from lib.DataTableMixin import DataTableMixin

class RawDataColumns(Columns):
    def __init__(self):
        self.addNumber("rawDataId")
        self.addString("path")
        self.addString("parameters")
        self.addString("query")
        self.addString("fragment")
        self.addBoolean("body")

class RawData(ndb.Model, CsvMixin, DataTableMixin):
    rawDataId = ndb.IntegerProperty()
    path = ndb.StringProperty(indexed=False)
    parameters = ndb.StringProperty(indexed=False)
    query = ndb.StringProperty(indexed=False)
    fragment = ndb.StringProperty(indexed=False)
    body = ndb.StringProperty(indexed=False)

    # fieldnames = ["rawDataId", "path", "parameters", "query", "fragment", "body"]
    
    @classmethod
    def queryRange(cls, start, end):
        debug("getRecentRawData start=%s end=%s" % (start, end))
        q = ndb.Query(kind="RawData")
        if start < end:
            q = q.order(cls.rawDataId)
            q = q.filter(cls.rawDataId >= start)
            q = q.filter(cls.rawDataId <= end)
            return q
        else:
            q = q.order(-cls.rawDataId)
            q = q.filter(cls.rawDataId <= start)
            q = q.filter(cls.rawDataId >= end)
            return q
    
    @classmethod
    def fetchRange(cls, start, end, limit=100):
        return cls.queryRange(start, end).fetch(keys_only=True, limit=100)
    
    @classmethod
    def queryRecent(cls):
        """returns iterator which yields ndb.Key object"""
        query = ndb.Query(kind="RawData")
        query = query.order(-cls.rawDataId)
        return query
    
    @classmethod
    def fetchRecent(cls, limit=100):
        return cls.queryRecent().fetch(keys_only=True, limit=limit)

    @classmethod
    def queryPeriod(cls, start_rawdata_id, end_rawdata_id):
        assert isinstance(start_rawdata_id, int)
        assert isinstance(end_rawdata_id, int)
        q = ndb.Query(kind="RawData")
        if start_rawdata_id >= end_rawdata_id:
            q = q.order(-cls.rawDataId)
            q = q.filter(cls.rawDataId <= start_rawdata_id)
            q = q.filter(cls.rawDataId >= end_rawdata_id)
        else:
            q = q.order(-cls.rawDataId)
            q = q.filter(cls.rawDataId <= end_rawdata_id)
            q = q.filter(cls.rawDataId >= start_rawdata_id)
        return q

    @classmethod
    def getLast(cls):
        keys = cls.fetchRecent(1)
        if len(keys) is 0: return None
        return keys[0].get()
    
    @classmethod
    def fetchByRawDataId(cls, raw_data_id):
        q = ndb.Query(kind="RawData").filter(cls.rawDataId == raw_data_id)
        keys = q.fetch(limit=2)
        assert len(keys) == 0 or len(keys) == 1
        if len(keys) == 0: return None
        return keys[0]

from unittest import TestCase
class _TestRawDataNdb(TestCase):
    
    TEST_RAWDATA_ID = 12345
    TEST_BODY = "bodybody"
    TEST_QUERY = "a=b&c=d"
    TEST_FRAGMENT = "fragmentfragment"
    TEST_PATH = "/a/b/c"
    TEST_PARAMETERS = ""

    def setUp(self):
        TestCase.setUp(self)
        from google.appengine.ext.testbed import Testbed
        self.testbed = Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
    
    def tearDown(self):
        self.testbed.deactivate()
        TestCase.tearDown(self)
        
    def testGetLast(self):
        key = RawData.fetchByRawDataId(self.TEST_RAWDATA_ID)
        if key is not None: key.delete()
        key = RawData.fetchByRawDataId(self.TEST_RAWDATA_ID)
        self.assertTrue(key is None)
        
        raw_data = RawData()
        raw_data.rawDataId = self.TEST_RAWDATA_ID 
        raw_data.path = self.TEST_PATH
        raw_data.parameters = self.TEST_PARAMETERS
        raw_data.query = self.TEST_QUERY
        raw_data.fragment = self.TEST_FRAGMENT
        raw_data.body = self.TEST_BODY
        raw_data.put()
        
        key = RawData.fetchByRawDataId(self.TEST_RAWDATA_ID)
        self.assertTrue(key is not None)
