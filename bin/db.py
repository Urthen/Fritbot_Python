'''Module to handle all DB communication.
A note to the unfamiliar, this acts as a singleton: All you have to do is call DB and start using it. It will be set up and shared everywhere.
'''

from twisted.python import log
from pymongo import Connection

import config

class Database(object):

    def __init__(self):
        self._connection = None
        self._db = None

    '''Return the database instance. Create it if it hasn't been yet.'''
    @property
    def db(self):
        if self._connection is None:
            log.msg("Establishing connection to database...")
            self._connection = Connection() #Because that's not ambiguous.
            self._db = self._connection[config.DB['name']]

        return self._db

    '''Get a single user by resource'''
    def getUserByUID(self, resource):
        mdbUser = self.db.users.find_one({"resource": resource})
        return mdbUser

db = Database()