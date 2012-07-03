'''Primary Fritbot class, which acts as the twistd service.
Connects to and handles all communication with the jabber server.'''

import sys, datetime, random, os

from twisted.internet import defer, reactor
from twisted.words.protocols.jabber import jid
from twisted.python import log

from wokkel import muc, xmppim

from fb.connectors.connector import Room, User
from fb.db import db
import config, fb.intent as intent

class FritBot(object):
    '''Main fritbot class, handles connecting to the server as well as input/output.'''
    
    rooms = {} 
    """Contains a dictionary of Room objects representing each room we're currently connected to, by uid."""

    _connection = None
    """Connection to an IM interface"""

    _instance = None
    _initialized = False

    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions relate to the initialization or shutdown of the bot.
    -----------------------------------------------------------------------------------------------------------------------------------------'''

    def __init__(self):
        '''Initialize the bot: Only called on when the bot is first launched, not subsequent reconnects.'''
        if self._initialized:
            raise Exception("Bot already initialized!")
        self._initialized = True
        log.msg("Initializing bot...")

        # Configure internals
        intent.service.link(self)
        intent.service.loadModules()

    def registerConnector(self, connector):
        log.msg("Connecting bot to requested chat service...")
        self._connection = connector

    def shutdown(self):
        '''Shut down the bot after a 2 second delay.'''
        if self._connection is not None and self._connection.parent is not None and self._connection.parent.stopService is not None:
            reactor.callLater(1, self._connection.parent.stopService)
        reactor.callLater(2, reactor.stop)

    def restart(self):
        '''Restart the bot after a 2 second delay.'''
        if self._connection is not None and self._connection.parent is not None and self._connection.parent.stopService is not None:
            reactor.callLater(1, self._connection.parent.stopService)
        reactor.callLater(2, self._restart)

    def _restart(self):
        '''Internal call to restart the bot.'''
        path = sys.executable
        os.execl(python, python, * sys.argv)

    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions relate to joining, creating, and leaving rooms.
    -----------------------------------------------------------------------------------------------------------------------------------------'''
        
    def initRoom(self, room):
        '''Joined a room, add it to the list.'''    
        log.msg("Connected to " + room.uid)
        room.active = True
        self.rooms[room.uid] = room
        
    def joinRoom(self, room, nick):
        '''Join a room'''
        self._connection.joinRoom(room, nick)                         
        
    def leaveRoom(self, room):
        '''Leave a room'''
        log.msg("Left " + room.uid)
        self._connection.leaveRoom(room)
        room.active = False
        del self.rooms[room.uid]


    def getRoom(self, uid):
        if uid in self.rooms:
            return self.rooms[uid]
        else:
            return None

    def getUser(self, uid):
        return self._connection.getUser(uid)

    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions directly relate to sending and recieving messages.
    -----------------------------------------------------------------------------------------------------------------------------------------'''

    def addHistory(self, room, user, nick, body, command = False):
        history = {
            "body": body,
            "user": {
                "nick": nick,
                "id": user["_id"]},
            "date": datetime.datetime.now(),
            "command": command
        }
        if room is not None:
            history['room'] = room['_id']

        db.db.history.insert(history)

    def receivedGroupChat(self, room, user, body, nick=None, history=False):
        '''Triggered when a group chat is recieved in a room the bot is in'''        

        if body is None:
            return

        body = body.encode('utf-8')

        #Validate that the user is NOT the bot itself!
        wasCommand = False
        if nick is None:
            nick = user['nick']
        
        log.msg("Group chat: <{0}/{1}>: {2}".format(room.uid, nick, body))
        
        wasCommand = intent.service.parseMessage(body, room, user)

        self.addHistory(room, user, nick, body, wasCommand)

    def receivedPrivateChat(self, user, body):
        '''Triggered when someone messages the bot directly.'''

        if body is None:
            return

        body = body.encode("utf-8")

        log.msg("Private chat: <{0}>: {1}".format(user['nick'], body))

        wasCommand = intent.service.parseMessage(body, None, user)

        self.addHistory(None, user, user['nick'], body, wasCommand)

bot = FritBot()
