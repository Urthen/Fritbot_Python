'''The original Jabber interface.
Connects to and handles all communication with the jabber server.'''

import sys, datetime

from twisted.internet import defer, reactor
from twisted.words.protocols.jabber import jid
from twisted.python import log

from wokkel import muc, xmppim, ping

import fb.fritbot as FritBot
from connector import IConnector, User, Room
from fb.db import db
import config, fb.intent as intent


CHAT = muc.MESSAGE + '[@type="chat"]'

class JRoom(Room):
    
    def __init__(self, room, interface):
        self._room = room
        self._interface = interface
        Room.__init__(self, room.roomJID.user, room.nick)

    def _send(self, message):
        self._interface.groupChat(self._room.occupantJID.userhostJID(), message)

    def setNick(self, nick):
        self._interface.nick(self._room.occupantJID.userhostJID(), nick)

    def setTopic(self, topic):
        self._interface.subject(self._room.occupantJID.userhostJID(), topic)

    @property
    def roster(self):
        return self._room.roster.keys()

class JUser(User):
    def __init__(self, jid, uid, nick, interface):
        self._interface = interface
        self.jid = jid
        User.__init__(self, uid, nick)

    def _send(self, message):
        self._interface.chat(self.jid, message)

class JabberConnector(IConnector, muc.MUCClient):
    '''Handles connections to individual rooms'''

    interface = None

    def __init__(self):
        '''Initialize the bot: Only called on when the bot is first launched, not subsequent reconnects.'''
        log.msg("Initializing Jabber connection...")

        IConnector.__init__(self)

        try:
            import OpenSSL
        except:
            log.msg("Error importing OpenSSL, you may (or may not) have trouble connecting to Jabber servers. Try installing OpenSSL for python.")

        self._presence = xmppim.PresenceClientProtocol()
        self._ping = ping.PingHandler()
        muc.MUCClient.__init__(self)

    def setHandlerParent(self, parent):
        '''Set handler parent of subhandlers'''
        muc.MUCClient.setHandlerParent(self, parent)
        self._presence.setHandlerParent(parent)
        self._presence.available(statuses={None: config.CONFIG["status"]})
        self._ping.setHandlerParent(parent)
       
    def connectionInitialized(self):
        '''Called on connect/reconnect. Attempts to re-join all existing rooms.'''
        muc.MUCClient.connectionInitialized(self)
        log.msg("MUC Connected.")
        self.xmlstream.addObserver(CHAT, self.receivedPrivateChat)
        
        for room in self.defaultConnections:
            self.joinRoom(room[0], room[1])

    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions relate to joining, creating, and leaving rooms.
    -----------------------------------------------------------------------------------------------------------------------------------------'''
        
    @defer.inlineCallbacks
    def initRoom(self, room):
        '''Perform post-join configuration.
        Configure rooms that need to be before others can join.'''


        log.msg("Attempting to connect to jabber room " + room.roomJID.user)
        r = db.getRoom(JRoom(room, self))
        room.info = r

        if room.locked:
            log.msg("New room created: " + room.roomJID.user)
            config_form = yield self.getConfiguration(room.roomJID)
            # set config default
            config_result = yield self.configure(room.roomJID)  
        FritBot.bot.initRoom(r)
        
    def joinRoom(self, room, nick):
        '''Join a room'''
        rjid = jid.internJID("%s@%s/%s" % (room, config.JABBER['confserver'], nick))
        self.join(rjid, nick).addCallback(self.initRoom)                           
        
    def leaveRoom(self, room):
        '''Leave a room'''
        self.leave(room._room.occupantJID.userhostJID())

        
    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions relate to user and nickname information.
    -----------------------------------------------------------------------------------------------------------------------------------------'''
        
    def userJoinedRoom(self, room, user):
        '''Called when a user joins a room'''
        self.userUpdatedStatus(room, user, None, None)
            
    def userUpdatedStatus(self, room, user, show, status):
        '''Called when a user changes their nickname'''

        if hasattr(user, 'entity') and user.entity is not None:
            ujid = user.entity
            uid = user.entity.user
        else:
            ujid = user.jid
            uid = user.jid.resource
        u = db.getUser(JUser(ujid, uid, user.nick, self))
        if hasattr(room, 'info'):
            r = room.info
        else:
            r = db.getRoom(JRoom(room, self))
        
        u.doNickUpdate(r, user.nick)

    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions directly relate to sending and recieving messages.
    -----------------------------------------------------------------------------------------------------------------------------------------'''

    def receivedGroupChat(self, room, user, message):
        '''Triggered when a group chat is recieved in a room the bot is in'''        
        #Validate that the user exists (catches some edge cases)
        if user is None:
            return

        if hasattr(user, 'entity') and user.entity is not None:
            ujid = user.entity
            uid = user.entity.user
        else:
            ujid = user.jid
            uid = user.jid.resource

        u = db.getUser(JUser(ujid, uid, user.nick, self))
        u.doNickUpdate(room.info, user.nick)

        #If we think this is from the bot itself, log it. If it's from someone else, try and handle it.
        if ujid.resource == config.JABBER['resource'] or ujid.resource == room.nick:
            FritBot.bot.addHistory(room.info, u, user.nick, message.body)
        else:
            FritBot.bot.receivedGroupChat(room.info, u, message.body, nick=user.nick)

    def receivedPrivateChat(self, msg):
        '''Triggered when someone messages the bot directly.'''
        if not msg.hasAttribute('from') or msg.body is None:
            return

        user_jid = jid.internJID(msg.getAttribute('from', ''))

        nick = user_jid.userhost().split('@', 1)[0]

        user = db.getUser(JUser(user_jid, user_jid.user, nick, self))

        FritBot.bot.receivedPrivateChat(user, unicode(msg.body))
