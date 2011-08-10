import re, datetime
from twisted.python import log

import config
from fb.db import db
from fb.commands import *
from fb.commands.util import cleanString

CAPTURE_BEGIN = ['"', "'"] #, '{', '(', '[']
CAPTURE_END = ['"', "'"] #, '}', ')', ']']

def cutString(text):
    words = text.split()
    output = []

    capturing = None
    captured = [] 

    for word in words:
        if capturing is None:
            if word[0] in CAPTURE_BEGIN:
                capturing = CAPTURE_END[CAPTURE_BEGIN.index(word[0])]

                if word[-1] == capturing:
                    output.append(word[1:-1])
                    capturing = None
                else:
                    captured.append(word[1:])
            else:
                output.append(word)
        else:
            if word[-1] == capturing:
                captured.append(word[:-1])
                output.append(' '.join(captured))
                captured = []
                capturing = None
            else:
                captured.append(word)
    if len(captured) > 0:
        output.append(' '.join(captured))
    return output
    
class IntentService(object):

    def __init__(self):
        self._refreshed = None
        self._intents = []
        self._bot = None

    def link(self, bot):
        '''Link the intent service to the bot.'''
        log.msg("Linking bot to intent service.")
        self._bot = bot

    def refreshIntents(self):
        '''Read intents from the database'''
        #refresh according to refresh guidelines
        if self._refreshed is None or (datetime.datetime.now() - self._refreshed) > datetime.timedelta(seconds=config.CONFIG['refresh']):
            log.msg("Intents need some refreshment...")
            self._refreshed = datetime.datetime.now()
            self._intents = []

            for command in db.db.commands.find():
                command['rexx'] = []
                for crex in command["command"]:
                    command['rexx'].append(re.compile("^" + crex + "$"))

                self._intents.append(command)

    def addressedToBot(self, text, room=None):
        '''Attempts to determine if a piece of text is addressed to the bot, as in, prefixed with its nickname.'''
        nicknames = [cleanString(config.CONFIG['name'])]
        nicknames.extend(config.CONFIG['nicknames'])
        if room is not None:
            nicknames.append(room["nick"])

        out = text.split(' ', 1)

        if cleanString(out[0]) in nicknames:
            return out[1]

    def parseMessage(self, body, room, user):
        '''Parse an incoming message.'''
        address = self.addressedToBot(body, room)

        if address is not None:
            return self.fetchCommand(address, room, user)
        elif room is None:
            return self.fetchCommand(body, room, user)
        return False, None

    def fetchCommand(self, text, room, user):
        '''Attempt to execute something that looks like a command.'''
        self.refreshIntents()

        words = cutString(text)

        log.msg("Lets do this command:", words)

        if words[0][0] == '>':
            newroom = words[0][1:]

            if newroom in self._bot.rooms:
                room = self._bot.rooms[newroom]
            else:
                return True, "I'm not in {0}...".format(words[0][1:])
            words = words[1:]

        if room is not None:
            #check to find any db updates in the background
            room.refresh()

        for intent in self._intents:
            for rex in intent['rexx']:
                for i in reversed(range(1, len(words) + 1)):
                    match = rex.match(' '.join(words[:i]))

                    if match is not None:
                        #We've found it! But... are we authorized to use it here?
                        if room is not None:
                            if len(set(room["auths"]) & set(intent["auth"])) == 0:
                                user.send("I can't do '{1}' in the {0} room.".format(room.uid, match.group()))
                                return True, None

                            if "squelch" in intent and intent["squelch"] and room.squelched:
                                user.send("I've been shut up in {0} for {2} longer, so I can't do '{1}'.".format(room.uid, match.group(), room.squelched))
                                return True, None

                        #Pull out any matched groups...
                        args = []
                        for x in range(1, 5):
                            try:
                                arg = match.group('arg' + str(x))
                            except:
                                #No arguments left (if there were any to begin with)
                                break
                            
                            ars.append(arg)

                        #Anything left is added to the args
                        args.extend(words[i:])

                        log.msg("Running command {0} with args {1}...".format(intent['function'], args))

                        out = eval(intent['function'])(self._bot, room, user, args)
                        #Anyway, whether or not it was a satisfactory result, we need to break the loop.
                        return True, out
        if room is not None:
            if room.squelched:
                user.send("I've been shut up in {0} for {2} longer, but I have no idea what '{1}' meant anyway.".format(room.uid, text, room.squelched))
                return False, None
            elif "vanity" not in room['auths']:
                user.send("I can't be spammy in {0}, but I have no idea what '{1}' meant anyway.".format(room.uid, text))
                return False, None
            return False, "[wat]"
        else:
            return False, "[wat]"


service = IntentService()