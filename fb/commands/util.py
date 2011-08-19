# Common Command Nonsense, not actual functions.

import re, random

import config
from fb.db import db

def cleanString(text):
    return re.sub("[^a-zA-Z0-9 ]", '', text.lower()).strip()

def getRandom(cursor):
    count = cursor.count()
    return cursor[random.randrange(count)]

def getSubset(cursor, min, max=None):
    if max is None:
        max = min

    out = []
    count = random.randrange(min, max + 1)
    subset = range(0, cursor.count())
    if count > len(subset):
        count = len(subset)

    while count > 0:
        count -= 1
        out.append(cursor[subset.pop(random.randrange(0, len(subset)))])

    return out

def inRoster(name, room=None, special=None):

    if special=="quotes":
        query = {'user.nick': {'$regex': name, '$options': 'i'}}
        quotes = db.db.history.find(query)
        if quotes.count() > 0:
            return True

    if room is not None:
        if name in room.roster:
            return [room.roster[name].info]
        
        for u in room.roster:
            if re.search('{0}'.format(name), u, flags=re.IGNORECASE):
                return [room.roster[u].info]

    user = db.db.users.find_one({'nick': name})
    if user:
        return [user]

    user = db.db.users.find({'nick': {'$regex': name, '$options': 'i'}})

    if user.count() == 0:
        user = db.db.users.find({'nicks.nicks': {'$regex': name, '$options': 'i'}})
    
    if user.count() > 0:
        users = []
        for u in user:
            users.append(u)
        return users
    
    return False
