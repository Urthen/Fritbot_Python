'''Primary Fritbot class, which acts as the twistd service.
Connects to and handles all communication with the jabber server.'''

import sys, datetime, random, os

from twisted.internet import defer, reactor
from twisted.words.protocols.jabber import jid
from twisted.python import log

from wokkel import muc, xmppim

from fb.interface.interface import Room, User, Interface
from fb.db import db
import config, fb.intent as intent  


class FritBot(object):
    '''Main fritbot class, handles connecting to the server as well as input/output.'''
    
    rooms = {} 
    """Contains a dictionary of Room objects representing each room we're currently connected to, by uid."""

    _connection = None
    """Connection to an IM interface"""

    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions relate to the initialization or shutdown of the bot.
    -----------------------------------------------------------------------------------------------------------------------------------------'''

    def __init__(self):
        '''Initialize the bot: Only called on when the bot is first launched, not subsequent reconnects.'''
        log.msg("Initializing bot...")

        # Configure internals
        for uid, nick in config.ROOMS.items():
            room = Room(uid, nick)
            self.rooms[uid] = room
        intent.service.link(self)

    def registerInterface(self, interface):
        log.msg("Connecting bot to interface...")
        self._connection = interface
       
    def connected(self):
        log.msg("Joining rooms...")
        roomlist = self.rooms.values()
        self.rooms = {}
        for room in roomlist:
            self._connection.joinRoom(room.uid, room['nick'])

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
        self.rooms[room.uid] = room
        
    def joinRoom(self, room, nick):
        '''Join a room'''
        self._connection.joinRoom(room, nick)                         
        
    def leaveRoom(self, room):
        '''Leave a room'''
        self._connection.leaveRoom(room)
        del self.rooms[room]


    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions directly relate to sending and recieving messages.
    -----------------------------------------------------------------------------------------------------------------------------------------'''

    def addUndo(self, room, user, undo):
        if room is not None:
            room.undostack.append(undo)
        else:
            user.undostack.append(undo)

    def addHistory(self, room, user, body, command):
        history = {
            "body": body,
            "user": {
                "nick": user['nick'],
                "id": user["_id"]},
            "date": datetime.datetime.now(),
            "command": command
        }
        if room is not None:
            history['room'] = room['_id']

        db.db.history.insert(history)

    def receivedGroupChat(self, room, user, body, history=False):
        '''Triggered when a group chat is recieved in a room the bot is in'''        
        #Validate that the user is NOT the bot itself!
        if user.uid.split('@', 1)[0] == config.JABBER['jid']:
            return

        body = body.encode("utf-8")

        log.msg(u"Group chat: <{0}/{1}>: {2}".format(room.uid, user['nick'], body))

        wasCommand, message = intent.service.parseMessage(body, room, user)
        if message is not None:
           room.send(message)

        self.addHistory(room, user, body, wasCommand)

    def receivedPrivateChat(self, user, body):
        '''Triggered when someone messages the bot directly.'''

        body = body.encode("utf-8")

        log.msg(u"Private chat: <{0}>: {1}".format(user['nick'], body))

        wasCommand, message = intent.service.parseMessage(body, None, user)
        if message is not None:
            user.send(message)

        self.addHistory(None, user, body, wasCommand)
