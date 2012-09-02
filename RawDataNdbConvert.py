import logging
from google.appengine.ext import deferred
from google.appengine.runtime import DeadlineExceededError
from RawData import RawData
from google.appengine.ext import db

class RawDataConvert(object):
    # Subclasses should replace this with a model class (eg, model.Person).
    #KIND = None

    # Subclasses can replace this with a list of (property, value) tuples to filter by.
    #FILTERS = []

    def __init__(self):
        self.batchPutEntityList = []
        self.batchDeleteEntityList = []

    def mapEntity(self, entity):
        assert isinstance(entity, RawData)
        """Updates a single entity.
        Implementers should return a tuple containing two iterables (to_update, to_delete).
        """
        entity.queryString = entity.query
        return ([entity],[])

    def finish(self):
        """Called when the mapper has finished, to allow for any final work to be done."""
        pass

    def _getQuery(self):
        """Returns a query over the specified kind, with any appropriate filters applied."""
        q = RawData.all()
        q.order("__key__")
        return q

    def run(self, batch_size=100):
        """Starts the mapper running."""
        self._continue(None, batch_size)

    def _batchWrite(self):
        """Writes updates and deletes entities in a batch."""
        if self.to_put:
            db.put(self.to_put)
            self.to_put = []
        if self.to_delete:
            db.delete(self.to_delete)
            self.to_delete = []

    def _continue(self, start_key, batch_size):
        q = self.get_query()
        # If we're resuming, pick up where we left off last time.
        if start_key:
            q.filter("__key__ >", start_key)
        # Keep updating records until we run out of time.
        try:
            # Steps over the results, returning each entity and its index.
            for i, entity in enumerate(q):
                map_updates, map_deletes = self.map(entity)
                self.to_put.extend(map_updates)
                self.to_delete.extend(map_deletes)
            # Do updates and deletes in batches.
            if (i + 1) % batch_size == 0:
                self._batch_write()
            # Record the last entity we processed.
                start_key = entity.key()
        except DeadlineExceededError:
            # Write any unfinished updates to the datastore.
            self._batch_write()
            # Queue a new task to pick up where we left off.
            deferred.defer(self._continue, start_key, batch_size)
            return
        self.finish()
        
def change(a, b, c=None):
    logging.info("Doing something expensive!")
    # Do your work here

# Somewhere else
deferred.defer(do_something_expensive, "Hello, world!", 42, c=True)