'''Quotes Commands'''

import random, re, datetime

from pymongo import ASCENDING, DESCENDING

from fb.db import db
import util

def sayQuotes(bot, room, user, nick, segment, min=1, max=1):
    if max < min:
        max = min

    if max > 10:
        return "Too many, jerkwad!"

    query = {'remembered': {'$exists': True}}
    if nick is not None:
        nickq = {'user.nick': {'$regex': nick, '$options': 'i'}}
        ids = util.inRoster(nick)
        if ids:
            idq = {'user.id': {'$in': map(lambda x: x['_id'], ids)}}
            query['$or'] = [nickq, idq]
        else:
            query.update(nickq)

    if segment is not None:
        query['body'] = {'$regex': segment, '$options': 'i'}  

    quotes = db.db.history.find(query)

    msg = None
    if quotes.count() == 0:
        msg = u"I can't find any quotes"
        if nick is not None:
            msg += u" for user {0}".format(nick)

        if segment is not None:
            msg += u" with string '{0}'".format(segment)
    else:        
        quotes = util.getSubset(quotes, min, max)
        lines = []
        for quote in quotes:
            lines.append(u"<{0}>: {1}".format(quote['user']['nick'], quote['body']))
        quotes = '\n'.join(lines)

        if room is not None:
            room.send(quotes)
        else:
            user.send(quotes)

    return msg

def parseQuoteArgs(args, room):
    user = None
    segment = None
    min = None
    max = None

    if len(args) >= 3 and ((args[1] == "to") or (args[1] in [',','-',':'])):
        try:
            min = int(args[0])
            max = int(args[2])
        except:
            pass #fuck em.
        args = args[3:]
    elif len(args) > 0:
        try:
            spl = re.split("[,\-:]", args[0], 1)
            min = int(spl[0])
            if len(spl) > 1:
                max = int(spl[1])
            else:
                max = int(spl[0])
            args = args[1:]
        except:
            pass #thats not a number.

    if len(args) > 0:
        if args[0] not in ['anyone', 'anybody', 'all', '*', '%']:
            tuser = util.inRoster(args[0], room, special="quotes")
            if tuser:
                user = args[0]
                args = args[1:]
        else:
            args = args[1:]

        if len(args) > 0:
            segment = ' '.join(args)

    return user, segment, min, max
    

def quote(bot, room, user, args):
    nick, segment, min, max = parseQuoteArgs(args, room)
    if min is None:
        min = 1
        max = 1

    return sayQuotes(bot, room, user, nick, segment, min, max)

def quotemash(bot, room, user, args):
    nick, segment, min, max = parseQuoteArgs(args, room)
    if min is None:
        min = 3
        max = 6

    return sayQuotes(bot, room, user, nick, segment, min, max)

def remember(bot, room, user, args):
    if room is None:
        return u"Can't remember private conversations!"

    if len(args) == 0:
        return u"Remember what, exactly?"

    tuser = util.inRoster(args[0], room)

    print tuser
    if tuser and len(tuser) >= 1:
        text = " ".join(args[1:])

        query = {"user.id": tuser[0]["_id"], "room": room.info["_id"], "body": {"$regex": text, '$options': 'i'}, "command": False}

        quote = db.db.history.find_one(query, sort=[("date", DESCENDING)])

        if quote:
            if quote['user']['id'] == user['_id']:
                return u"Sorry, {0}, but you can't quote yourself! Try saying someone funnier and maybe someone else will remember you.".format(user['nick'])
            if "remembered" in quote:
                return u"Sorry, {0}, I already knew about <{1}>: {2}".format(user["nick"], quote['user']["nick"], quote["body"].encode("utf-8"))
            else:
                quote["remembered"] = {"user": user["_id"], "nick": user["nick"], "time": datetime.datetime.now()}
                db.db.history.save(quote)
                return u"Ok, {0}, remembering <{1}>: {2}".format(user["nick"], quote['user']['nick'], quote["body"].encode("utf-8"))
        else:
            return u"Sorry, {0}, I haven't heard anything like '{1}' by {2}.".format(user["nick"], text, tuser[0]["nick"])

    elif not tuser:
        return u"Hrm, the name {0} doesn't ring any bells.".format(args[0])
    else:
        return u"Sorry, {0} isn't unique enough. Too many users matched!".format(args[0])
