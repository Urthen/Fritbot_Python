import re, datetime, random
from twisted.python import log

import config
from fb.db import db
from fb.commands import *
from fb.commands.util import cleanString, sendMsg

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
        self._modules = {}

        self._listeners = []
        self._commands = []

        self._bot = None

        #TODO: Deprecate these.
        self._intentsrefreshed = None
        self._listeners_oldrefreshed = None
        self._intents = []
        self._commands_old = []
        self._listeners_old = []

    def link(self, bot):
        '''Link the intent service to the bot.'''
        log.msg("Linking bot to intent service.")
        self._bot = bot

    def registerModule(self, module, name):
        log.msg("Registering module:", name)
        moduleobject = module.module
        self._modules[name] = moduleobject
        moduleobject.register()

    def registerCommand(self, keywords, function, module, name, description):
        if type(keywords) != type([]):
            keywords = [keywords]

        rexwords = []
        for word in keywords:
            rexwords.append(re.compile('^' + word + "$", re.I))

        command = {'keywords': rexwords, 'function': function, 'name': name, 'description': description, 'module': module}
        self._commands.append(command)

    def registerListener(self, patterns, function, module, name, description):
        if type(patterns) != type([]):
            patterns = [patterns]

        rexwords = []
        for word in patterns:
            rexwords.append(re.compile('^' + word + "$", re.I))

        listener = {'patterns': rexwords, 'function': function, 'name': name, 'description': description, 'module': module}
        self._listeners.append(listener)

    def addressedToBot(self, text, room=None):
        '''Attempts to determine if a piece of text is addressed to the bot, as in, prefixed with its nickname.'''
        #TODO: Fix this so it works with multiple-work nicknames!
        nicknames = [cleanString(config.CONFIG['name'])]
        nicknames.extend(config.CONFIG['nicknames'])
        if room is not None:
            nicknames.append(room["nick"])

        out = text.split(' ', 1)

        if cleanString(out[0]) in nicknames and len(out) > 1:
            return out[1]

    def parseMessage(self, body, room, user):
        '''Parse an incoming message.'''
        address = self.addressedToBot(body, room)

        if address is not None:
            body = address
        
        #Check to see if this is a command
        if address is not None or room is None:
            words = cutString(body)

            for command in self._commands:
                for rex in command['keywords']:
                    for i in reversed(range(1, len(words) + 1)):
                        match = rex.search(cleanString(' '.join(words[:i])))

                        if match is not None:
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
                            handled = command['function'](self._bot, room, user, args)
                            if handled:
                                return True, None

        for listener in self._listeners:
            for rex in listener['patterns']:
                match = rex.search(cleanString(body))

                if match is not None:
                    handled = listener['function'](self._bot, room, user, match)
                    if handled:
                        return False, None

        # Support for existing commands.
        iscommand = False
        out = None

        if address is not None:
            iscommand, out = self.fetchCommand(address, room, user)
        elif room is None:
            iscommand, out = self.fetchCommand(body, room, user)

        return iscommand, out


#####################################################################################################################################################################
# Everything below this line is going to be removed once new-style commands are finished.
#####################################################################################################################################################################

    def refreshIntents(self):
        '''Read intents from the database'''
        #refresh intents according to refresh guidelines
        if self._intentsrefreshed is None or (datetime.datetime.now() - self._intentsrefreshed) > datetime.timedelta(seconds=config.CONFIG['refresh']):
            log.msg("Intents need some refreshment...")
            self._intentsrefreshed = datetime.datetime.now()
            self._intents = []

            for command in db.db.commands.find():
                command['rexx'] = []
                for crex in command["command"]:
                    command['rexx'].append(re.compile("^" + crex + "$"))

                self._intents.append(command)

    def refreshResponses(self):
        if self._listeners_oldrefreshed is None or (datetime.datetime.now() - self._listeners_oldrefreshed) > datetime.timedelta(seconds=config.CONFIG['refresh']):
            log.msg("Responses need some refreshment...")
            self._listeners_oldrefreshed = datetime.datetime.now()
            self._listeners_old = []

            for response in db.db.intents.find():
                self._listeners_old.append(response)

    def fetchResponse(self, body, room, user):
        '''Attempt to negotiate a response based on context.'''
        self.refreshResponses()

        options = []
        if room is None:
            route = user
        else:
            route = room

        for response in self._listeners_old:
            if route.disallowed(response['auths']):
                continue

            for trigger in response['triggers']:
                if type(trigger) == type(u''):
                    match = re.search(trigger, body, re.I)
                    if match is not None:
                        options.append((match, response))
                elif type(trigger) == type({}):
                    print "Dictionary triggers not implemented yet."
                else:
                    print "Type of trigger", choice, "was not recognized."
            
        selections = []
        length = 0            
        for option in options:
            optlen = len(option[0].group(0))
            if optlen > length:
                selections = [option]
                length = optlen
            elif optlen == length:
                selections.append(option)

        if len(selections) > 0:
            selection = random.choice(selections)
            actionset = random.choice(selection[1]['actions']) 
            for action in actionset['list']:
                for key in action:
                    if key == "say":
                        route.send(action[key])
            return True
        else:
            return False
            

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
                            if room.disallowed(intent["auth"]):
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
            elif room.allowed("mean"):
                return False, "I'm sorry, {0}, I don't know what '{1}' means.".format(user['nick'], text)
            else:
                return False, "[wat]"
        else:
            return False, "I'm sorry, I don't know what '{0}' means.".format(text)

service = IntentService()

