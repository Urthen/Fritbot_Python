# -*- test-case-name: wokkel.test.test_muc -*-
#
# Copyright (c) Ralph Meijer.
# See LICENSE for details.

"""
XMPP Multi-User Chat protocol.

This protocol is specified in
U{XEP-0045<http://www.xmpp.org/extensions/xep-0045.html>}.
"""
from dateutil.tz import tzutc

from zope.interface import implements

from twisted.internet import defer
from twisted.words.protocols.jabber import jid, error, xmlstream
from twisted.words.xish import domish

from wokkel import data_form, generic, xmppim
from wokkel.delay import Delay, DelayMixin
from wokkel.subprotocols import XMPPHandler
from wokkel.iwokkel import IMUCClient

# Multi User Chat namespaces
NS_MUC = 'http://jabber.org/protocol/muc'
NS_MUC_USER = NS_MUC + '#user'
NS_MUC_ADMIN = NS_MUC + '#admin'
NS_MUC_OWNER = NS_MUC + '#owner'
NS_MUC_ROOMINFO = NS_MUC + '#roominfo'
NS_MUC_CONFIG = NS_MUC + '#roomconfig'
NS_MUC_REQUEST = NS_MUC + '#request'
NS_MUC_REGISTER = NS_MUC + '#register'

NS_REGISTER = 'jabber:iq:register'

MESSAGE = '/message'
PRESENCE = '/presence'

GROUPCHAT = MESSAGE +'[@type="groupchat"]'

DEFER_TIMEOUT = 30 # basic timeout is 30 seconds



class _FormRequest(generic.Request):
    """
    Base class for form exchange requests.
    """
    requestNamespace = None
    formNamespace = None

    def __init__(self, recipient, sender=None, options=None):
        if options is None:
            stanzaType = 'get'
        else:
            stanzaType = 'set'

        generic.Request.__init__(self, recipient, sender, stanzaType)
        self.options = options


    def toElement(self):
        element = generic.Request.toElement(self)

        query = element.addElement((self.requestNamespace, 'query'))
        if self.options is None:
            # This is a request for the configuration form.
            form = None
        elif not self.options:
            form = data_form.Form(formType='cancel')
        else:
            form = data_form.Form(formType='submit',
                                  formNamespace=self.formNamespace)
            form.makeFields(self.options)

        if form:
            query.addChild(form.toElement())

        return element



class ConfigureRequest(_FormRequest):
    """
    Configure MUC room request.

    http://xmpp.org/extensions/xep-0045.html#roomconfig
    """

    requestNamespace = NS_MUC_OWNER
    formNamespace = NS_MUC_CONFIG



class RegisterRequest(_FormRequest):
    """
    Register request.

    http://xmpp.org/extensions/xep-0045.html#register
    """

    requestNamespace = NS_REGISTER
    formNamespace = NS_MUC_REGISTER



class AdminItem(object):
    """
    Item representing role and/or affiliation for admin request.
    """

    def __init__(self, affiliation=None, role=None, entity=None, nick=None,
                       reason=None):
        self.affiliation = affiliation
        self.role = role
        self.entity = entity
        self.nick = nick
        self.reason = reason


    def toElement(self):
        element = domish.Element((NS_MUC_ADMIN, 'item'))

        if self.entity:
            element['jid'] = self.entity.full()

        if self.nick:
            element['nick'] = self.nick

        if self.affiliation:
            element['affiliation'] = self.affiliation

        if self.role:
            element['role'] = self.role

        if self.reason:
            element.addElement('reason', content=self.reason)

        return element


    @classmethod
    def fromElement(Class, element):
        item = Class()

        if element.hasAttribute('jid'):
            item.entity = jid.JID(element['jid'])

        item.nick = element.getAttribute('nick')
        item.affiliation = element.getAttribute('affiliation')
        item.role = element.getAttribute('role')

        for child in element.elements(NS_MUC_ADMIN, 'reason'):
            item.reason = unicode(child)

        return item



class AdminStanza(generic.Request):
    """
    An admin request or response.
    """

    childParsers = {(NS_MUC_ADMIN, 'query'): '_childParser_query'}

    def toElement(self):
        element = generic.Request.toElement(self)
        element.addElement((NS_MUC_ADMIN, 'query'))

        if self.items:
            for item in self.items:
                element.query.addChild(item.toElement())

        return element


    def _childParser_query(self, element):
        self.items = []
        for child in element.elements(NS_MUC_ADMIN, 'item'):
            self.items.append(AdminItem.fromElement(child))



class DestructionRequest(generic.Request):
    """
    Room destruction request.

    @param reason: Optional reason for the destruction of this room.
    @type reason: C{unicode}.

    @param alternate: Optional room JID of an alternate venue.
    @type alternate: L{jid.JID}

    @param password: Optional password for entering the alternate venue.
    @type password: C{unicode}
    """

    stanzaType = 'set'

    def __init__(self, recipient, sender=None, reason=None, alternate=None,
                       password=None):
        generic.Request.__init__(self, recipient, sender)
        self.reason = reason
        self.alternate = alternate
        self.password = password


    def toElement(self):
        element = generic.Request.toElement(self)
        element.addElement((NS_MUC_OWNER, 'query'))
        element.query.addElement('destroy')

        if self.alternate:
            element.query.destroy['jid'] = self.alternate.full()

            if self.password:
                element.query.destroy.addElement('password',
                                                 content=self.password)

        if self.reason:
            element.query.destroy.addElement('reason', content=self.reason)

        return element



class GroupChat(xmppim.Message, DelayMixin):
    """
    A groupchat message.
    """

    stanzaType = 'groupchat'

    def toElement(self, legacyDelay=False):
        """
        Render into a domish Element.

        @param legacyDelay: If C{True} send the delayed delivery information
        in legacy format.
        """
        element = xmppim.Message.toElement(self)

        if self.delay:
            element.addChild(self.delay.toElement())

        return element



class PrivateChat(xmppim.Message):
    """
    A chat message.
    """

    stanzaType = 'chat'



class InviteMessage(xmppim.Message):

    def __init__(self, recipient=None, sender=None, invitee=None, reason=None):
        xmppim.Message.__init__(self, recipient, sender)
        self.invitee = invitee
        self.reason = reason


    def toElement(self):
        element = xmppim.Message.toElement(self)

        child = element.addElement((NS_MUC_USER, 'x'))
        child.addElement('invite')
        child.invite['to'] = self.invitee.full()

        if self.reason:
            child.invite.addElement('reason', content=self.reason)

        return element



class HistoryOptions(object):
    """
    A history configuration object.

    @ivar maxchars: Limit the total number of characters in the history to "X"
        (where the character count is the characters of the complete XML
        stanzas, not only their XML character data).
    @type maxchars: C{int}

    @ivar maxstanzas: Limit the total number of messages in the history to "X".
    @type mazstanzas: C{int}

    @ivar seconds: Send only the messages received in the last "X" seconds.
    @type seconds: C{int}

    @ivar since: Send only the messages received since the datetime specified.
        Note that this must be an offset-aware instance.
    @type since: L{datetime.datetime}
    """
    attributes = ['maxchars', 'maxstanzas', 'seconds', 'since']

    def __init__(self, maxchars=None, maxstanzas=None, seconds=None,
                       since=None):
        self.maxchars = maxchars
        self.maxstanzas = maxstanzas
        self.seconds = seconds
        self.since = since


    def toElement(self):
        """
        Returns a L{domish.Element} representing the history options.
        """
        element = domish.Element((NS_MUC, 'history'))

        for key in self.attributes:
            value = getattr(self, key, None)
            if value is not None:
                if key == 'since':
                    stamp = value.astimezone(tzutc())
                    element[key] = stamp.strftime('%Y%m%dT%H:%M:%SZ')
                else:
                    element[key] = str(value)

        return element



class User(object):
    """
    A user/entity in a multi-user chat room.
    """

    def __init__(self, nick, entity=None, user=None):
        self.nick = nick
        self.entity = entity
        self.user = user
        self.affiliation = 'none'
        self.role = 'none'

        self.status = None
        self.show = None



class Room(object):
    """
    A Multi User Chat Room.

    An in memory object representing a MUC room from the perspective of
    a client.

    @ivar roomIdentifier: The Room ID of the MUC room.
    @type roomIdentifier: C{unicode}

    @ivar service: The server where the MUC room is located.
    @type service: C{unicode}

    @ivar nick: The nick name for the client in this room.
    @type nick: C{unicode}

    @ivar state: The status code of the room.
    @type state: L{int}

    @ivar occupantJID: The JID of the occupant in the room. Generated from
        roomIdentifier, service, and nick.
    @type occupantJID: L{jid.JID}
    """


    def __init__(self, roomIdentifier, service, nick, state=None):
        """
        Initialize the room.
        """
        self.roomIdentifier = roomIdentifier
        self.service = service
        self.setNick(nick)
        self.state = state

        self.status = 0

        self.roster = {}


    def setNick(self, nick):
        self.occupantJID = jid.internJID(u"%s@%s/%s" % (self.roomIdentifier,
                                                        self.service,
                                                        nick))
        self.nick = nick


    def addUser(self, user):
        """
        Add a user to the room roster.

        @param user: The user object that is being added to the room.
        @type user: L{User}
        """
        self.roster[user.nick] = user


    def inRoster(self, user):
        """
        Check if a user is in the MUC room.

        @param user: The user object to check.
        @type user: L{User}
        """

        return user.nick in self.roster


    def getUser(self, nick):
        """
        Get a user from the room's roster.

        @param nick: The nick for the user in the MUC room.
        @type nick: C{unicode}
        """
        return self.roster.get(nick)


    def removeUser(self, user):
        """
        Remove a user from the MUC room's roster.

        @param user: The user object to check.
        @type user: L{User}
        """
        if self.inRoster(user):
            del self.roster[user.nick]



class BasicPresence(xmppim.AvailabilityPresence):
    """
    Availability presence sent from MUC client to service.

    @type history: L{HistoryOptions}
    """
    history = None
    password = None

    def toElement(self):
        element = xmppim.AvailabilityPresence.toElement(self)

        muc = element.addElement((NS_MUC, 'x'))
        if self.password:
            muc.addElement('password', content=self.password)
        if self.history:
            muc.addChild(self.history.toElement())

        return element



class UserPresence(xmppim.AvailabilityPresence):
    """
    Availability presence sent from MUC service to client.
    """

    statusCode = None
    jid = None

    childParsers = {(NS_MUC_USER, 'x'): '_childParser_mucUser'}

    def _childParser_mucUser(self, element):
        for child in element.elements():
            if child.uri != NS_MUC_USER:
                continue
            elif child.name == 'status':
                self.statusCode = child.getAttribute('code')
            elif child.name == 'item':
                self.jid = child.getAttribute('jid')
            # TODO: item, destroy



class VoiceRequest(xmppim.Message):
    """
    Voice request message.
    """

    def toElement(self):
        element = xmppim.Message.toElement(self)

        # build data form
        form = data_form.Form('submit', formNamespace=NS_MUC_REQUEST)
        form.addField(data_form.Field(var='muc#role',
                                      value='participant',
                                      label='Requested role'))
        element.addChild(form.toElement())

        return element



class MUCClient(xmppim.BasePresenceProtocol):
    """
    Multi-User Chat client protocol.

    This is a subclass of L{XMPPHandler} and implements L{IMUCCLient}.

    @ivar _rooms: Collection of occupied rooms, keyed by the bare JID of the
                  room. Note that a particular entity can only join a room once
                  at a time.
    @type _rooms: C{dict}
    """

    implements(IMUCClient)

    timeout = None

    presenceTypeParserMap = {
                'error': generic.ErrorStanza,
                'available': UserPresence,
                'unavailable': UserPresence,
                }

    def __init__(self, reactor=None):
        XMPPHandler.__init__(self)

        self._rooms = {}
        self._deferreds = []

        if reactor:
            self._reactor = reactor
        else:
            from twisted.internet import reactor
            self._reactor = reactor


    def connectionInitialized(self):
        """
        Called when the XML stream has been initialized.

        It initializes several XPath events to handle MUC stanzas that come in.
        After those are initialized the method L{initialized} is called to
        signal that we have finished.
        """
        xmppim.BasePresenceProtocol.connectionInitialized(self)
        self.xmlstream.addObserver(GROUPCHAT, self._onGroupChat)
        self.initialized()


    def _addRoom(self, room):
        """
        Add a room to the room collection.

        Rooms are stored by the JID of the room itself. I.e. it uses the Room
        ID and service parts of the Room JID.

        @note: An entity can only join a particular room once.
        """
        roomJID = room.occupantJID.userhostJID()
        self._rooms[roomJID] = room


    def _getRoom(self, roomJID):
        """
        Grab a room from the room collection.

        This uses the Room ID and service parts of the given JID to look up
        the L{Room} instance associated with it.

        @type occupantJID: L{jid.JID}
        """
        return self._rooms.get(roomJID)


    def _removeRoom(self, occupantJID):
        """
        Delete a room from the room collection.
        """
        roomJID = occupantJID.userhostJID()
        if roomJID in self._rooms:
            del self._rooms[roomJID]


    def unavailableReceived(self, presence):
        """
        Unavailable presence was received.

        If this was received from a MUC room occupant JID, that occupant has
        left the room.
        """

        occupantJID = presence.sender

        if occupantJID:
            self._userLeavesRoom(occupantJID)


    def errorReceived(self, presence):
        """
        Error presence was received.

        If this was received from a MUC room occupant JID, we conclude the
        occupant has left the room.
        """
        occupantJID = presence.sender

        if occupantJID:
            self._userLeavesRoom(occupantJID)


    def _userLeavesRoom(self, occupantJID):
        # when a user leaves a room we need to update it
        room = self._getRoom(occupantJID.userhostJID())
        if room is None:
            # not in the room yet
            return
        # check if user is in roster
        user = room.getUser(occupantJID.resource)
        if user is None:
            return
        if room.inRoster(user):
            room.removeUser(user)
            self.userLeftRoom(room, user)


    def availableReceived(self, presence):
        """
        Available presence was received.
        """

        occupantJID = presence.sender

        if presence.jid is not None:
            occupantJID.actual = presence.jid
        
        if not occupantJID:
            return

        # grab room
        room = self._getRoom(occupantJID.userhostJID())
        if room is None:
            # not in the room yet
            return

        user = self._changeUserStatus(room, occupantJID, presence.status,
                                      presence.show)

        if room.inRoster(user):
            # we changed status or nick
            if presence.statusCode:
                room.status = presence.statusCode # XXX
            else:
                self.userUpdatedStatus(room, user, presence.show,
                                       presence.status)
        else:
            room.addUser(user)
            self.userJoinedRoom(room, user)


    def _onGroupChat(self, element):
        """
        A group chat message has been received from a MUC room.

        There are a few event methods that may get called here.
        L{receivedGroupChat}, L{receivedHistory} or L{receivedHistory}.
        """
        message = GroupChat.fromElement(element)

        occupantJID = message.sender
        if not occupantJID:
            return

        roomJID = occupantJID.userhostJID()

        room = self._getRoom(roomJID)
        if room is None:
            # not in the room yet
            return

        if occupantJID.resource:
            user = room.getUser(occupantJID.resource)
        else:
            # This message is from the room itself.
            user = None

        if message.subject:
            self.receivedSubject(room, message.subject)
        elif message.delay is None:
            self.receivedGroupChat(room, user, message)
        else:
            self.receivedHistory(room, user, message)


    def _joinedRoom(self, presence):
        """
        We have presence that says we joined a room.
        """
        roomJID = presence.sender.userhostJID()

        # change the state of the room
        room = self._getRoom(roomJID)
        room.state = 'joined'

        # grab status
        if presence.statusCode:
            room.status = presence.statusCode

        return room


    def _leftRoom(self, presence):
        """
        We have presence that says we left a room.
        """
        occupantJID = presence.sender

        # change the state of the room
        self._removeRoom(occupantJID)

        return True


    def initialized(self):
        """
        Client is initialized and ready!
        """
        pass


    def userJoinedRoom(self, room, user):
        """
        User has joined a MUC room.

        This method will need to be modified inorder for clients to
        do something when this event occurs.

        @param room: The room the user has joined.
        @type room: L{Room}

        @param user: The user that joined the MUC room.
        @type user: L{User}
        """
        pass


    def userLeftRoom(self, room, user):
        """
        User has left a room.

        This method will need to be modified inorder for clients to
        do something when this event occurs.

        @param room: The room the user has joined.
        @type room: L{Room}

        @param user: The user that left the MUC room.
        @type user: L{User}
        """
        pass


    def userUpdatedStatus(self, room, user, show, status):
        """
        User Presence has been received.

        This method will need to be modified inorder for clients to
        do something when this event occurs.
        """
        pass


    def receivedSubject(self, room, subject):
        """
        This method will need to be modified inorder for clients to
        do something when this event occurs.
        """
        pass


    def receivedGroupChat(self, room, user, message):
        """
        A groupchat message was received.

        @param room: The room the message was received from.
        @type room: L{Room}

        @param user: The user that sent the message, or C{None} if it was a
            message from the room itself.
        @type user: L{User}

        @param message: The message.
        @type message: L{GroupChat}
        """
        pass


    def receivedHistory(self, room, user, message):
        """
        A groupchat message from the room's discussion history was received.

        This is identical to L{receivedGroupChat}, with the delayed delivery
        information (timestamp and original sender) in C{message.delay}. For
        anonymous rooms, C{message.delay.sender} is the room's address.

        @param room: The room the message was received from.
        @type room: L{Room}

        @param user: The user that sent the message, or C{None} if it was a
            message from the room itself.
        @type user: L{User}

        @param message: The message.
        @type message: L{GroupChat}
        """
        pass


    def sendDeferred(self, stanza):
        """
        Send presence stanza, adding a deferred with a timeout.

        @param stanza: The presence stanza to send over the wire.
        @type stanza: L{generic.Stanza}

        @param timeout: The number of seconds to wait before the deferred is
            timed out.
        @type timeout: L{int}

        The deferred object L{defer.Deferred} is returned.
        """
        d = defer.Deferred()

        def onResponse(element):
            if element.getAttribute('type') == 'error':
                d.errback(error.exceptionFromStanza(element))
            else:
                d.callback(UserPresence.fromElement(element))

        def onTimeout():
            d.errback(xmlstream.TimeoutError("Timeout waiting for response."))

        call = self._reactor.callLater(DEFER_TIMEOUT, onTimeout)

        def cancelTimeout(result):
            if call.active():
                call.cancel()

            return result

        d.addBoth(cancelTimeout)

        query = "/presence[@from='%s' or (@from='%s' and @type='error')]" % (
                stanza.recipient.full(), stanza.recipient.userhost())
        self.xmlstream.addOnetimeObserver(query, onResponse, priority=1)
        self.xmlstream.send(stanza.toElement())
        return d


    def configure(self, roomJID, options):
        """
        Configure a room.

        @param roomJID: The room to configure.
        @type roomJID: L{jid.JID}

        @param options: A mapping of field names to values, or C{None} to cancel.
        @type options: C{dict}
        """
        if not options:
            options = False
        request = ConfigureRequest(recipient=roomJID, options=options)
        return self.request(request)


    def getConfiguration(self, roomJID):
        """
        Grab the configuration from the room.

        This sends an iq request to the room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @return: A deferred that fires with the room's configuration form as
            a L{data_form.Form} or C{None} if there are no configuration
            options available.
        """
        def cb(response):
            form = data_form.findForm(response.query, NS_MUC_CONFIG)
            return form

        request = ConfigureRequest(recipient=roomJID, options=None)
        d = self.request(request)
        d.addCallback(cb)
        return d


    def join(self, service, roomIdentifier, nick, history=None):
        """
        Join a MUC room by sending presence to it.

        @param server: The server where the room is located.
        @type server: C{unicode}

        @param room: The room name the entity is joining.
        @type room: C{unicode}

        @param nick: The nick name for the entitity joining the room.
        @type nick: C{unicode}

        @param history: The maximum number of history stanzas you would like.

        @return: A deferred that fires when the entity is in the room or an
                 error has occurred.
        """
        room = Room(roomIdentifier, service, nick, state='joining')
        self._addRoom(room)

        presence = BasicPresence(recipient=room.occupantJID)
        if history:
            presence.history = HistoryOptions(maxstanzas=history)

        d = self.sendDeferred(presence)
        d.addCallback(self._joinedRoom)
        return d


    def _changeUserStatus(self, room, occupantJID, status, show):
        """
        Change the user status in a room.
        """

        # check if user is in roster
        user = room.getUser(occupantJID.resource)
        if user is None: # create a user that does not exist
            if hasattr(occupantJID, 'actual'):
                jid = occupantJID.actual
            else:
                jid = occupantJID.userhostJID()
            user = User(occupantJID.resource, user=jid.split('/')[0])

        if status is not None:
            user.status = unicode(status)
        if show is not None:
            user.show = unicode(show)

        return user


    def _changed(self, presence, occupantJID):
        """
        Callback for changing the nick and status.
        """
        room = self._getRoom(occupantJID.userhostJID())
        self._changeUserStatus(room, occupantJID, presence.status, presence.show)

        return room


    def nick(self, roomJID, nick):
        """
        Change an entity's nick name in a MUC room.

        See: http://xmpp.org/extensions/xep-0045.html#changenick

        @param roomJID: The JID of the room, i.e. without a resource.
        @type roomJID: L{jid.JID}

        @param nick: The new nick name within the room.
        @type nick: C{unicode}
        """
        room = self._getRoom(roomJID)

        # Change the nickname
        room.setNick(nick)

        # Create presence
        presence = BasicPresence(recipient=room.occupantJID)

        d = self.sendDeferred(presence)
        d.addCallback(self._changed, room.occupantJID)
        return d


    def leave(self, roomJID):
        """
        Leave a MUC room.

        See: http://xmpp.org/extensions/xep-0045.html#exit

        @param roomJID: The Room JID of the room to leave.
        @type roomJID: L{jid.JID}
        """
        room = self._getRoom(roomJID)

        presence = xmppim.AvailabilityPresence(recipient=room.occupantJID,
                                               available=False)

        d = self.sendDeferred(presence)
        d.addCallback(self._leftRoom)
        return d


    def status(self, roomJID, show=None, status=None):
        """
        Change user status.

        See: http://xmpp.org/extensions/xep-0045.html#changepres

        @param roomJID: The Room JID of the room.
        @type roomJID: L{jid.JID}

        @param show: The availability of the entity. Common values are xa,
            available, etc
        @type show: C{unicode}

        @param show: The current status of the entity.
        @type show: C{unicode}
        """
        room = self._getRoom(roomJID)

        presence = BasicPresence(recipient=room.occupantJID,
                                 show=show, status=status)

        d = self.sendDeferred(presence)
        d.addCallback(self._changed, room.occupantJID)
        return d


    def _sendMessage(self, message, children=None):
        """
        Send a message.
        """
        element = message.toElement()
        if children:
            for child in children:
                element.addChild(child)

        self.xmlstream.send(element)


    def groupChat(self, roomJID, body, children=None):
        """
        Send a groupchat message.
        """
        message = GroupChat(recipient=roomJID, body=body)
        self._sendMessage(message, children=children)


    def chat(self, occupantJID, body, children=None):
        """
        Send a private chat message to a user in a MUC room.

        See: http://xmpp.org/extensions/xep-0045.html#privatemessage

        @param occupantJID: The Room JID of the other user.
        @type occupantJID: L{jid.JID}
        """
        message = PrivateChat(recipient=occupantJID, body=body)
        self._sendMessage(message, children=children)


    def invite(self, roomJID, invitee, reason=None):
        """
        Invite a xmpp entity to a MUC room.

        See: http://xmpp.org/extensions/xep-0045.html#invite

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @param invitee: The entity that is being invited.
        @type invitee: L{jid.JID}

        @param reason: The reason for the invite.
        @type reason: C{unicode}
        """
        message = InviteMessage(recipient=roomJID, invitee=invitee,
                                reason=reason)
        self._sendMessage(message)


    def password(self, roomJID, password):
        """
        Send a password to a room so the entity can join.

        See: http://xmpp.org/extensions/xep-0045.html#enter-pw

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @param password: The MUC room password.
        @type password: C{unicode}
        """
        presence = BasicPresence(roomJID)
        presence.password = password

        self.xmlstream.send(presence.toElement())


    def register(self, roomJID, options):
        """
        Send a request to register for a room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @param options: A mapping of field names to values, or C{None} to
            cancel.
        @type options: C{dict}
        """
        request = RegisterRequest(recipient=roomJID, options=options)
        return self.request(request)


    def _getAffiliationList(self, roomJID, affiliation):
        """
        Send a request for an affiliation list in a room.
        """
        def cb(response):
            stanza = AdminStanza.fromElement(response)
            return stanza.items

        request = AdminStanza(recipient=roomJID, stanzaType='get')
        request.items = [AdminItem(affiliation=affiliation)]
        d = self.request(request)
        d.addCallback(cb)
        return d


    def _getRoleList(self, roomJID, role):
        """
        Send a request for a role list in a room.
        """
        def cb(response):
            stanza = AdminStanza.fromElement(response)
            return stanza.items

        request = AdminStanza(recipient=roomJID, stanzaType='get')
        request.items = [AdminItem(role=role)]
        d = self.request(request)
        d.addCallback(cb)
        return d


    def getMemberList(self, roomJID):
        """
        Get the member list of a room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}
        """
        return self._getAffiliationList(roomJID, 'member')


    def getAdminList(self, roomJID):
        """
        Get the admin list of a room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}
        """
        return self._getAffiliationList(roomJID, 'admin')


    def getBanList(self, roomJID):
        """
        Get an outcast list from a room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}
        """
        return self._getAffiliationList(roomJID, 'outcast')


    def getOwnerList(self, roomJID):
        """
        Get an owner list from a room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}
        """
        return self._getAffiliationList(roomJID, 'owner')


    def getModeratorList(self, roomJID):
        """
        Get the moderator list of a room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}
        """
        d = self._getRoleList(roomJID, 'moderator')
        return d


    def getRegisterForm(self, roomJID):
        """
        Grab the registration form for a MUC room.

        @param room: The room jabber/xmpp entity id for the requested
            registration form.
        @type room: L{jid.JID}
        """
        iq = RegisterRequest(self.xmlstream)
        iq['to'] = roomJID.userhost()
        return iq.send()


    def destroy(self, roomJID, reason=None, alternate=None, password=None):
        """
        Destroy a room.

        @param roomJID: The JID of the room.
        @type roomJID: L{jid.JID}

        @param reason: The reason for the destruction of the room.
        @type reason: C{unicode}

        @param alternate: The JID of the room suggested as an alternate venue.
        @type alternate: L{jid.JID}

        """
        def destroyed(iq):
            self._removeRoom(roomJID)

        request = DestructionRequest(recipient=roomJID, reason=reason,
                                     alternate=alternate, password=password)

        d = self.request(request)
        d.addCallback(destroyed)
        return d


    def subject(self, roomJID, subject):
        """
        Change the subject of a MUC room.

        See: http://xmpp.org/extensions/xep-0045.html#subject-mod

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @param subject: The subject you want to set.
        @type subject: C{unicode}
        """
        msg = GroupChat(roomJID.userhostJID(), subject=subject)
        self.xmlstream.send(msg.toElement())


    def voice(self, roomJID):
        """
        Request voice for a moderated room.

        @param roomJID: The room jabber/xmpp entity id.
        @type roomJID: L{jid.JID}
        """
        message = VoiceRequest(recipient=roomJID)
        self.xmlstream.send(message.toElement())


    def history(self, roomJID, messages):
        """
        Send history to create a MUC based on a one on one chat.

        See: http://xmpp.org/extensions/xep-0045.html#continue

        @param roomJID: The room jabber/xmpp entity id.
        @type roomJID: L{jid.JID}

        @param messages: The history to send to the room as an ordered list of
                         message, represented by a dictionary with the keys
                         C{'stanza'}, holding the original stanza a
                         L{domish.Element}, and C{'timestamp'} with the
                         timestamp.
        @type messages: L{list} of L{domish.Element}
        """

        for message in messages:
            stanza = message['stanza']
            stanza['type'] = 'groupchat'

            delay = Delay(stamp=message['timestamp'])

            sender = stanza.getAttribute('from')
            if sender is not None:
                delay.sender = jid.JID(sender)

            stanza.addChild(delay.toElement())

            stanza['to'] = roomJID.userhost()
            if stanza.hasAttribute('from'):
                del stanza['from']

            self.xmlstream.send(stanza)


    def _setAffiliation(self, roomJID, entity, affiliation,
                              reason=None, sender=None):
        """
        Send a request to change an entity's affiliation to a MUC room.
        """
        request = AdminStanza(recipient=roomJID, sender=sender,
                               stanzaType='set')
        item = AdminItem(entity=entity, affiliation=affiliation, reason=reason)
        request.items = [item]
        return self.request(request)


    def _setRole(self, roomJID, nick, role,
                       reason=None, sender=None):
        """
        Send a request to change an occupant's role in a MUC room.
        """
        request = AdminStanza(recipient=roomJID, sender=sender,
                               stanzaType='set')
        item = AdminItem(nick=nick, role=role, reason=reason)
        request.items = [item]
        return self.request(request)


    def modifyAffiliationList(self, roomJID, entities, affiliation,
                                    sender=None):
        """
        Modify an affiliation list.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @param entities: The list of entities to change for a room.
        @type entities: L{list} of L{jid.JID}

        @param affiliation: The affilation to the entities will acquire.
        @type affiliation: C{unicode}

        @param sender: The entity sending the request.
        @type sender: L{jid.JID}

        """
        request = AdminStanza(recipient=roomJID, sender=sender,
                               stanzaType='set')
        request.items = [AdminItem(entity=entity, affiliation=affiliation)
                         for entity in entities]

        return self.request(request)


    def grantVoice(self, roomJID, nick, reason=None, sender=None):
        """
        Grant voice to an entity.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @param nick: The nick name for the user in this room.
        @type nick: C{unicode}

        @param reason: The reason for granting voice to the entity.
        @type reason: C{unicode}

        @param sender: The entity sending the request.
        @type sender: L{jid.JID}
        """
        return self._setRole(roomJID, nick=nick,
                             role='participant',
                             reason=reason, sender=sender)


    def revokeVoice(self, roomJID, nick, reason=None, sender=None):
        """
        Revoke voice from a participant.

        This will disallow the entity to send messages to a moderated room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @param nick: The nick name for the user in this room.
        @type nick: C{unicode}

        @param reason: The reason for revoking voice from the entity.
        @type reason: C{unicode}

        @param sender: The entity sending the request.
        @type sender: L{jid.JID}
        """
        return self._setRole(roomJID, nick=nick, role='visitor',
                             reason=reason, sender=sender)


    def grantModerator(self, roomJID, nick, reason=None, sender=None):
        """
        Grant moderator privileges to a MUC room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @param nick: The nick name for the user in this room.
        @type nick: C{unicode}

        @param reason: The reason for granting moderation to the entity.
        @type reason: C{unicode}

        @param sender: The entity sending the request.
        @type sender: L{jid.JID}
        """
        return self._setRole(roomJID, nick=nick, role='moderator',
                             reason=reason, sender=sender)


    def ban(self, roomJID, entity, reason=None, sender=None):
        """
        Ban a user from a MUC room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @param entity: The bare JID of the entity to be banned.
        @type entity: L{jid.JID}

        @param reason: The reason for banning the entity.
        @type reason: C{unicode}

        @param sender: The entity sending the request.
        @type sender: L{jid.JID}
        """
        return self._setAffiliation(roomJID, entity, 'outcast',
                                    reason=reason, sender=sender)


    def kick(self, roomJID, nick, reason=None, sender=None):
        """
        Kick a user from a MUC room.

        @param roomJID: The bare JID of the room.
        @type roomJID: L{jid.JID}

        @param nick: The occupant to be banned.
        @type nick: C{unicode}

        @param reason: The reason given for the kick.
        @type reason: C{unicode}

        @param sender: The entity sending the request.
        @type sender: L{jid.JID}
        """
        return self._setRole(roomJID, nick, 'none',
                             reason=reason, sender=sender)
