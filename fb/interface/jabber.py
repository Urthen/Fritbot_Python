'''Primary Fritbot class, which acts as the twistd service.
Connects to and handles all communication with the jabber server.'''

import sys, datetime, random

from twisted.internet import defer, reactor
from twisted.words.protocols.jabber import jid
from twisted.python import log

from wokkel import muc, xmppim

from interface import Interface, User, Room
from fb.db import db
import config, fb.intent as intent

class JRoom(Room):
    
    def __init__(self, room, interface):
        self._room = room
        self._interface = interface
        Room.__init__(self, room.name, room.nick)

    def _send(self, message):
        self._interface.groupChat(self._room.entity_id, message)

    def setNick(self, nick):
        self._interface.nick(self._room.entity_id, nick)

class JUser(User):
    def __init__(self, uid, nick, interface):
        self._interface = interface
        User.__init__(self, uid, nick)

    def _send(self, message):
        self._interface.chat(jid.internJID(self.uid), message)

class JabberInterface(Interface, muc.MUCClient):
    '''Connect to a Jabber server.'''

    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions relate to the initialization or shutdown of the bot.
    -----------------------------------------------------------------------------------------------------------------------------------------'''

    def __init__(self, bot):
        '''Initialize the bot: Only called on when the bot is first launched, not subsequent reconnects.'''
        log.msg("Initializing Jabber interface...")
        Interface.__init__(self, bot)
        muc.MUCClient.__init__(self)

    def connectionInitialized(self):
        '''Add observers to the XML stream for some custom fritbotty nonsense not supported by default on wokkel'''
        self.xmlstream.addObserver(muc.PRESENCE+"[not(@type) or @type='available']/x", self._onXPresence)
        self.xmlstream.addObserver(muc.PRESENCE+"[@type='unavailable']", self._onUnavailablePresence)
        self.xmlstream.addObserver(muc.PRESENCE+"[@type='error']", self._onPresenceError)
        self.xmlstream.addObserver(muc.GROUPCHAT, self._onGroupChat)
        self.xmlstream.addObserver(muc.SUBJECT, self._onSubject)
        self.xmlstream.addObserver(muc.CHAT_BODY, self.receivedPrivateChat)

        self.initialized()
       
    def initialized(self):
        '''Called on connect/reconnect. Attempts to re-join all existing rooms.'''
        log.msg("Connected to Jabber service.")

        # Create xmpp presence subhandler
        self._presence = xmppim.PresenceClientProtocol()
        self._presence.setHandlerParent(self.parent)
        self._presence.available(statuses={None: config.CONFIG["status"]})

        self.bot.connect()

    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions relate to joining, creating, and leaving rooms.
    -----------------------------------------------------------------------------------------------------------------------------------------'''
        
    @defer.inlineCallbacks
    def initRoom(self, room):
        '''Perform post-join configuration.
        Configure rooms that need to be before others can join.'''


        log.msg("Attempting to connect to jabber room " + room.name)
        r = db.getRoom(JRoom(room, self))
        room.info = r

        if int(room.status) == muc.STATUS_CODE_CREATED:
            log.msg("New room created: " + room.name)
            userhost = rjid(room).userhost()
            config_form = yield self.getConfigureForm(userhost)
            
            # set config default
            config_result = yield self.configure(userhost)  
        reactor.callFromThread(self.fbInitRoom, r)
        
    def fbInitRoom(self, room):
        '''Joined a room, get the configuration or create default configuration'''
        self.bot.initRoom(room)
        
    def joinRoom(self, room, nick):
        '''Join a room'''
        self.join(config.JABBER['server'], room, nick).addCallback(self.initRoom)                           
        
    def leaveRoom(self, room):
        '''Leave a room'''
        self.leave(room._room.entity_id)

        
    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions relate to user and nickname information.
    -----------------------------------------------------------------------------------------------------------------------------------------'''
        
    def userJoinedRoom(self, room, user):
        '''Called when a user joins a room'''
        self.userUpdatedStatus(room, user, None, None)
            
    def userUpdatedStatus(self, room, user, show, status):
        '''Called when a user changes their nickname'''
        u = db.getUser(JUser(user.resource, user.nick, self))
        if hasattr(room, 'info'):
            r = room.info
        else:
            r = db.getRoom(JRoom(room, self))
        
        self.doNickUpdate(u, r, user.nick)


    '''----------------------------------------------------------------------------------------------------------------------------------------
    The following functions directly relate to sending and recieving messages.
    -----------------------------------------------------------------------------------------------------------------------------------------'''

    def receivedGroupChat(self, room, user, body):
        '''Triggered when a group chat is recieved in a room the bot is in'''        
        #Validate that the user exists (catches some edge cases)
        if user is None:
            return

        u = db.getUser(JUser(user.resource, user.nick, self))

        self.doNickUpdate(u, room.info, user.nick)

        self.bot.receivedGroupChat(room.info, u, body)

    def receivedPrivateChat(self, msg):
        '''Triggered when someone messages the bot directly.'''
        if not msg.hasAttribute('from'):
            return

        user_jid = jid.internJID(msg.getAttribute('from', ''))

        resource = user_jid.userhost()
        nick = user_jid.userhost().split('@', 1)[0]

        user = db.getUser(JUser(resource, nick, self))

        self.bot.receivedPrivateChat(user, unicode(msg.body))
