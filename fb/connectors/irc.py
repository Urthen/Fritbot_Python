'''Fritbot IRC interface
Connects to and handles all communication with an IRC server.'''

import sys, datetime
from twisted.internet import defer, reactor
from twisted.python import log
from twisted.words.protocols import irc
from twisted.internet import protocol

import fb.fritbot as FritBot
from connector import User, Room
from fb.db import db
import config, fb.intent as intent

class IRCChannel(Room):
    
    def __init__(self, channel, interface):
        self._interface = interface
        Room.__init__(self, channel)

    def _send(self, message):
        self._interface.notice(self.uid, message)

    def setNick(self, nick):
        raise NotImplementedError("setNick() is not available for IRC.")

class IRCUser(User):
    def __init__(self, nick, interface):
        self._interface = interface
        User.__init__(self, nick, nick)

    def _send(self, message):
        self._interface.notice(self.uid, message)

class IRCInterface(irc.IRCClient):
    '''Handles connections to individual rooms'''

    def __init__(self):
        '''Initialize the bot: Called when first launched and subsequent reconnects.'''
        log.msg("Initializing IRC interface...")
        #LOL NOPE

    def _get_nickname(self):
        return config.IRC['nick']
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        log.msg("MUC Connected.")
        FritBot.bot.connected()

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        FritBot.bot.initRoom(room)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            msg = "%s: I am a log bot" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))

class IRCInterfaceFactory(protocol.ClientFactory):
    protocol = IRCInterface

    def __init__(self, channel, nickname='YourMomDotCom'):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)
