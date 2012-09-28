'''Module to handle all DB communication.
A note to the unfamiliar, this acts as a singleton: All you have to do is call DB and start using it. It will be set up and shared everywhere.
'''

import datetime

from twisted.python import log
import pymongo
from pymongo import Connection, errors as PyMongoErrors
from bson.objectid import ObjectId

import config

ASCENDING = pymongo.ASCENDING
DESCENDING = pymongo.DESCENDING

OID = ObjectId

class Database(object):

    _connection = None
    _db = None
    _roomCache = {}
    _roomIDCache = {}
    _userCache = {}


    '''Return the database instance. Create it if it hasn't been yet.'''
    @property
    def db(self):
        if self._connection is None:
            log.msg("Establishing connection to database...")
            try:
                self._connection = Connection() #Because that's not ambiguous.
            except PyMongoErrors.AutoReconnect:
                raise AssertionError("Error connecting to the MongoDB instance. Is mongod running?")

            self._db = self._connection[config.DB['name']]

        return self._db

    def __getattr__(self, collection):
        return getattr(self.db, collection)

    def getRoom(self, room):
        if room.uid in self._roomCache:
            room = self._roomCache[room.uid]
            #print "found in cache", room.uid, room._refreshed
        else:
            log.msg("Room not found in cache and will be loaded: {0}".format(room.uid))
            self._roomCache[room.uid] = room

        room.refresh()

        return room

    def getRoomByUID(self, uid):
        if uid in self._roomCache:
            room = self._roomCache[uid]
            room.refresh()
            return room
        else:
            return None

    def getRoomInfo(self, rid):
        info = None
        if rid in self._roomIDCache:
            info = self._roomIDCache[rid]
            if (datetime.datetime.now() - info['_refreshed']) > datetime.timedelta(seconds=config.CONFIG["refresh"]):
                info = self._db.rooms.find_one({'_id': rid})
                if info:
                    info['_refreshed'] = datetime.datetime.now()
                    self._roomIDCache[rid] = info
                else:
                    del self._roomIDCache[rid]
        else:
            info = self._db.rooms.find_one({'_id': rid})
            if info:
                info['_refreshed'] = datetime.datetime.now()
                self._roomIDCache[rid] = info
        
        return info


    def getUser(self, user):

        if user.uid in self._userCache:
            user = self._userCache[user.uid]
            #print "found in cache", user.uid, user._refreshed
        else:
            log.msg("User not found in cache and will be loaded: {0}".format(user.uid))
            self._userCache[user.uid] = user
        user.refresh()

        return user  

db = Database()