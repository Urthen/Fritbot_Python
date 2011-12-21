# I LOVE FRIT BOT YES I DO
# I LOVE FRIT BOT MORE THAN YOU

import datetime

from twisted.python import log
from twisted.internet import reactor

import config
from fb.db import db

def shutdown(bot, room, user, args):
    if user['admin'] == True:
        log.msg(u"Shutting down by request from {0}.".format(user['nick']))
        bot.shutdown()
        return u"Ok, shutting down momentarily."
    else:
        return u"Not gonna happen, {0}.".format(user['nick'])

def undo(bot, room, user, args):
    if room is not None:
        stack = room.undostack
    else:
        stack = user.undostack

    if len(stack) == 0:
        return u"Nothing to undo!"

    if args is None or len(args) == 0:
        args = ['last']

    if args[0] == 'list':
        undos = []
        for undo in reversed(stack):
            undos.append('{0}: {1}'.format(len(undos) + 1, undo['message']))
        return '\n'.join(undos)
    else:
        if args[0] == 'last' or args[0] == 'that':
            num = len(stack) - 1
        else:
            try:
                num = int(args[0])
            except:
                return u"{0} isn't a valid answer!".format(args[0])

        undo = stack[num]
        undone, message = undo['function'](bot, room, user, undo)
        if undone == True:
            stack.pop(num)

        return message

def join(bot, room, user, args):
    '''Joins a room. Can be undone.'''

    if len(args) == 0:
        return "Join where?"

    join = args.pop(0)
    nick = config.CONFIG['name']

    if len(args) >= 2:
        if args[0] == "as":
            nick = args[1]

    bot.joinRoom(join, nick)
    bot.addUndo(room, user, {'function': undoJoin, 'message': 'Joined {0}'.format(join), 'room': join})
    return u"Ok, I've jumped into {0}!".format(join)

def undoJoin(bot, room, user, args):
    '''Undoes [join] by leaving the room.'''
    try:
        bot.leaveRoom(args['room'])
    except:
        return True, u"Looks like I was already gone anyway..."
    return True, u"Ok, backed out of {0}...".format(args['room'])

def leave(bot, room, user, args):
    '''Leaves a room. Can be used to leave other rooms with >channel functionality.'''
    if len(args):
        if args[0] in bot.rooms:
            room = bot.rooms[args[0]]
        else:
            return "I'm not in {0}...".format(args[0])
    bot.leaveRoom(room)
    user.send(u"Ok, I've left {0}.".format(room.uid))
    bot.addUndo(room, user, {'function': undoLeave, 'message': 'Left {0}'.format(room.uid), 'room': room.uid})

def undoLeave(bot, room, user, args):
    try:
        bot.joinRoom(args['room'], args['nick'])
    except:
        return True, u"Something went wrong rejoining the room.. maybe I'm already there?"
    return True, u"Ok, I'm back in {0}!".format(args['room'])

def quiet(bot, room, user, args):
    '''Squelches the bot for the given room.'''

    if room is None:
        return "This isn't a chat room!"

    room["squelched"] = datetime.datetime.now() + datetime.timedelta(minutes=5);
    room.save()
    return "Shut up for 5 minutes."

def unquiet(bot, room, user, args):

    if room is None:
        return "This isn't a chat room!"

    room["squelched"] = datetime.datetime.now() - datetime.timedelta(minutes=5);
    room.save()
    return "And we're back."

def allow(bot, room, user, args, doundo=False):
    if room is None:
        ret = (False, u"This isn't a chat room!")
    elif len(args) < 1:
        ret = (False, u"Must specify a permission...")
    elif user['admin'] == True:
        auths = set(room["auths"]) | set(args)
        room["auths"] = list(auths)
        room.save()

        if not doundo:
            msg = u"Allowed {0}".format(repr(args))
            undo = {'function': undoAllow, 'args': args, 'room': room, 'message': msg}
            bot.addUndo(room, user, undo)

        ret = (True, u"Ok, allowing the following authorizations: {0}".format(repr(args)))
    else:
        ret = (False, u"Not gonna happen, {0}.".format(user['nick']))

    if doundo:
        return ret
    else:
        return ret[1]

def undoAllow(bot, room, user, args):
    return disallow(bot, args["room"], user, args["args"], True)

def disallow(bot, room, user, args, doundo=False):
    if room is None:
        ret = (False, u"This isn't a chat room!")
    elif len(args) < 1:
        ret = (False, u"Must specify a permission...")
    elif user['admin'] == True:
        auths = set(room["auths"]) - set(args)
        room["auths"] = list(auths)
        room.save()

        if not doundo:
            msg = u"Disallowed {0}".format(repr(args))
            undo = {'function': undoDisallow, 'args': args, 'room': room, 'message': msg}
            bot.addUndo(room, user, undo)

        ret = (True, u"Ok, disallowing the following authorizations: {0}".format(repr(args)))
    else:
        ret = (False, u"Not gonna happen, {0}.".format(user['nick']))

    if doundo:
        return ret
    else:
        return ret[1]

def undoDisallow(bot, room, user, args):
    return allow(bot, args["room"], user, args["args"], True)

def auths(bot, room, user, args):
    if room is None:
        return u"Users don't have individual permissions within the context of Fritbot."
    return u"I currently have the following authorizations for the {0} room: {1}".format(room.uid, repr(room["auths"]))
