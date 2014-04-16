import datetime, random

from twisted.internet import defer, reactor
from twisted.python import log

from fb.db import db
from fb.config import cfg

class Route(object):
    '''A valid route for sending messages. Currently, this could be a room or a user.'''

    TYPE = "None"
    '''What type of route this is. Should be changed by subclasses.'''

    uid = None
    '''Unique identifier for this route.'''

    info = {}
    '''MongoDB Information for this route.'''

    _collection = None
    '''MongoDB Collection representing all objects for this route type.'''

    _refreshed = None
    '''When was this route last refreshed?'''

    active = False

    ratelimit = {}
    
    def __getitem__(self, key):
        '''Getter for contained MongoDB info object. Returns None if key is not found.'''
        if key in self.info:
            data = self.info[key]

            if type(data) == type("") or type(data) == type(u""):
                return data.encode('utf-8')
            else:
                return data
        else:
            return None

    def __setitem__(self, key, value):
        '''Setter for contained MongoDB info object.'''
        self.info[key] = value

    def __init__(self, uid):
        '''Initialize a route with given unique identifier.'''
        self.uid = uid

    def __repr__(self):
        return "<{0} {1}>".format(self.TYPE, self.uid)

    def send(self, message, delay=False):
        '''Attempt to send a message with optional delay'''
        if not self.active:
            log.warn("Attempted to send a message to inactive %s: %s", self.TYPE, self.uid)
            return

        if message is None or message == "":
            log.warn("Attempted to send an empty messsage")
            return

        if type(message) == type(u""):
            message = message.encode('utf-8')

        time = 0.2
        if type(delay) is int:
            time = delay
        elif delay is True:
            time = 1.5 + random.random() * 2

        log.msg("Sending <{0}>: {1}".format(self.uid, message))
        reactor.callLater(time, self._send, unicode(message, 'utf-8'))

    def _send(self, message):
        '''Template to actually send a message via this route. Must be implemented in a subclass.'''
        raise NotImplementedError("_send() is not implemented in this Route instance.")

    def needsRefresh(self):
        if self._refreshed is None:
            return True
        else:
            return (datetime.datetime.now() - self._refreshed) > datetime.timedelta(seconds=cfg.mongo.refresh)

    def refresh(self):
        '''Template to refresh the mongodb information for this route. Must be implemented in a subclass.'''
        raise NotImplementedError("refresh() is not implemented in this Route instance.")

    def save(self):
        '''Save the MongoDB info for this route.'''
        if self._collection is not None:
            self._collection.save(self.info)
        else:
            raise NotImplementedError("save() cannot be run when _collection is not set. It should be set by the subclass.")

    def allowed(self, permissions):
        if type(permissions) == type([]):
            return len(set(self.info["auths"]) & set(permissions)) > 0
        else:
            return permissions in self["auths"]

    def disallowed(self, permissions):
        return not self.allowed(permissions)


class Room(Route):

    TYPE = "Room"

    roster = {}
    '''Dict of User objects currently in this room, by uid'''

    def __init__(self, uid, nick=cfg.bot.name):
        self['nick'] = nick
        self._collection = db.db.rooms
        Route.__init__(self, uid)

    def refresh(self):
        if not self.needsRefresh():
            return

        self._refreshed = datetime.datetime.now()
        mdbRoom = db.db.rooms.find_one({"name": self.uid})

        if mdbRoom is None:
            log.msg("Not found, creating new room in DB.")
            mdbRoom = {
                "name": self.uid,
                "nick": self['nick'],
                "auths": ["core"]
            }
            
            db.db.rooms.insert(mdbRoom)

        self.info = mdbRoom

    def setNick(self, nick):
        self['nick'] = nick

    def setTopic(self, topic):
        raise NotImplementedError("setTopic() must be implemented by a sub-class.")

    @property
    def roster(self):
        raise NotImplementedError("roster must be implemented by a sub-class.")

    @property
    def squelched(self):
        if 'squelched' in self.info and self["squelched"] > datetime.datetime.now():
            seconds = (self["squelched"] - datetime.datetime.now()).seconds
            minutes = int(seconds / 60)
            seconds = seconds - (minutes * 60)
            if minutes > 0:
                return "{0} minute(s)".format(minutes)
            else:
                return "{0} second(s)".format(seconds)
        else:
            return False

class User(Route):

    TYPE = "User"

    active = True
    '''Always assume we can talk to the user. Probably not the best assumption, but whatever.'''

    def __init__(self, uid, nick):
        self['nick'] = nick
        self._collection = db.db.users
        Route.__init__(self, uid)

    def refresh(self):
        if not self.needsRefresh():
            return

        mdbUser= db.db.users.find_one({"resource": self.uid})

        if mdbUser is None:
            log.msg("{0} not found, creating new user in DB.".format(self.uid))
            mdbUser = {
                "resource": self.uid,
                "nick": self['nick']
            }
            
            db.db.users.insert(mdbUser)

        self.info = mdbUser

    @property
    def banned(self):
        return self.info.get("banned", False)

    @property
    def admin(self):
        return self.uid in cfg.super_admins or self.info.get("admin", False)
    
    def allowed(self, permissions):
        return True #everything's allowed when you're having fun alone

    def doNickUpdate(self, room, nick):
        '''Update user and room nicknames, if appropriate.
        Helper function that should be called by sub-classes whenever a new user connects to a room, or a user of a room changes nicknames.'''

        if "nicks" in self.info:
            found = False
            for r in self["nicks"]:
                if r["room"] == room.uid:
                    if nick not in r["nicks"]:
                        r["nicks"].append(nick)
                    found = True
                    break
            if not found:
                self["nicks"].append({"room": room.uid, "nicks": [nick]})
        else:
            self["nicks"] = [{"room": room.uid, "nicks": [self['nick']]}]

        if "nick" not in self.info:
            self["nick"] = user.nick

        self.save()
