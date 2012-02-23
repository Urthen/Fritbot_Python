'''The original Jabber interface.
Connects to and handles all communication with the jabber server.'''

import sys, datetime

from twisted.internet import defer, reactor
from twisted.words.protocols.jabber import jid
from twisted.python import log

from wokkel import muc, xmppim, ping

import fb.fritbot as FritBot
from interface import Interface, User, Room
from fb.db import db
import config, fb.intent as intent


CHAT = muc.MESSAGE + '[@type="chat"]'
STATUS_CODE_CREATED = 201

class JRoom(Room):
    
    def __init__(self, room, interface):
        self._room = room
        self._interface = interface
        Room.__init__(self, room.roomIdentifier, room.nick)

    def _send(self, message):
        self._interface.groupChat(self._room.occupantJID.userhostJID(), message)

    def setNick(self, nick):
        self._interface.nick(self._room.occupantJID.userhostJID(), nick)

class JUser(User):
    def __init__(self, user, nick, interface):
        self._interface = interface
        User.__init__(self, user, nick)

    def _send(self, message):
        self._interface.chat(jid.internJID(self.uid), message)

class JabberInterface(Interface, muc.MUCClient):
    '''Handles connections to individual rooms'''

    interface = None

    def __init__(self):
        '''Initialize the bot: Only called on when the bot is first launched, not subsequent reconnects.'''
        log.msg("Initializing Jabber interface...")

        Interface.__init__(self)

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
       
    def initialized(self):
        '''Called on connect/reconnect. Attempts to re-join all existing rooms.'''
        log.msg("MUC Connected.")
        self.xmlstream.addObserver(CHAT, self.receivedPrivateChat)
        FritBot.bot.connected()

    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions relate to joining, creating, and leaving rooms.
    -----------------------------------------------------------------------------------------------------------------------------------------'''
        
    @defer.inlineCallbacks
    def initRoom(self, room):
        '''Perform post-join configuration.
        Configure rooms that need to be before others can join.'''


        log.msg("Attempting to connect to jabber room " + room.roomIdentifier)
        r = db.getRoom(JRoom(room, self))
        room.info = r

        if int(room.status) == STATUS_CODE_CREATED:
            log.msg("New room created: " + room.roomIdentifier)
            userhost = rjid(room).userhost()
            config_form = yield self.getConfigureForm(userhost)
            
            # set config default
            config_result = yield self.configure(userhost)  
        reactor.callFromThread(self.fbInitRoom, r)
        
    def fbInitRoom(self, room):
        '''Joined a room, get the configuration or create default configuration'''
        FritBot.bot.initRoom(room)
        
    def joinRoom(self, room, nick):
        '''Join a room'''
        self.join(config.JABBER['server'], room, nick).addCallback(self.initRoom)                           
        
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
        u = db.getUser(JUser(user.user, user.nick, self))
        if hasattr(room, 'info'):
            r = room.info
        else:
            r = db.getRoom(JRoom(room, self))
        
        self.doNickUpdate(u, r, user.nick)


    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions directly relate to sending and recieving messages.
    -----------------------------------------------------------------------------------------------------------------------------------------'''

    def receivedGroupChat(self, room, user, message):
        '''Triggered when a group chat is recieved in a room the bot is in'''        
        #Validate that the user exists (catches some edge cases)
        if user is None:
            return

        u = db.getUser(JUser(user.user, user.nick, self))

        self.doNickUpdate(u, room.info, user.nick)

        FritBot.bot.receivedGroupChat(room.info, u, message.body, nick=user.nick)

    def receivedPrivateChat(self, msg):
        '''Triggered when someone messages the bot directly.'''
        if not msg.hasAttribute('from') or msg.body is None:
            return

        user_jid = jid.internJID(msg.getAttribute('from', ''))

        resource = user_jid.userhost()
        nick = user_jid.userhost().split('@', 1)[0]

        user = db.getUser(JUser(resource, nick, self))

        FritBot.bot.receivedPrivateChat(user, unicode(msg.body))