'''Primary Fritbot class, which acts as the twistd service.
Connects to and handles all communication with the jabber server.'''

import sys, datetime, random

from twisted.internet import defer, reactor
from twisted.words.protocols.jabber import jid
from twisted.python import log

from wokkel import muc, xmppim

from interface import Room, User, Interface
from db import db
import config, intent      


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
        print "Initializing bot..."

        # Configure internals
        for uid, nick in config.ROOMS.items():
            room = Room(uid, nick)
            self.rooms[uid] = room
        intent.service.link(self)

    def registerInterface(self, interface):
        print "Connecting bot to interface..."
        self._connection = interface
       
    def connect(self):
        print "Joining rooms..."
        roomlist = self.rooms.values()
        self.rooms = {}
        for room in roomlist:
            self._connection.joinRoom(room.uid, room['nick'])

    def shutdown(self):
        '''Shut down the bot after a 2 second delay.'''
        if self._connection is not None and self._connection.parent is not None and self._connection.parent.stopService is not None:
            reactor.callLater(1, self._connection.parent.stopService)
        reactor.callLater(2, reactor.stop)

    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions relate to joining, creating, and leaving rooms.
    -----------------------------------------------------------------------------------------------------------------------------------------'''
        
    def initRoom(self, room):
        '''Joined a room, add it to the list.'''    
        print "Connected to " + room.uid               
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

    def receivedGroupChat(self, room, user, body):
        '''Triggered when a group chat is recieved in a room the bot is in'''        
        #Validate that the user is NOT the bot itself!
        if user['nick'].lower() == room['nick'].lower():
            return

        body = body.encode("utf-8")

        log.msg("Group chat: <{0}/{1}>: {2}".format(room.uid, user['nick'], body))

        wasCommand, message = intent.service.parseMessage(body, room, user)
        if message is not None:
           room.send(message)

        self.addHistory(room, user, body, wasCommand)

    def receivedPrivateChat(self, user, body):
        '''Triggered when someone messages the bot directly.'''

        body = body.encode("utf-8")

        log.msg("Private chat: <{0}>: {1}".format(user['nick'], body))

        wasCommand, message = intent.service.parseMessage(body, None, user)
        if message is not None:
            user.send(message)

        self.addHistory(None, user, body, wasCommand)