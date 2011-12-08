# Common Command Nonsense, not actual functions.

import re, random
from operator import itemgetter

import config
from fb.db import db

MULT_EXACT = 1.0
MULT_CASE_WRONG = 0.9
MULT_PART_WORD = 0.8
MULT_PART_FIRST = 0.6
MULT_PART_OTHER = 0.4

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

def sendMsg(room, user, message):
    if room is not None:
        room.send(message)
    else:
        user.send(message)

def inRoster(name, room=None, special=None):

    if special=="quotes":
        query = {'user.nick': {'$regex': name, '$options': 'i'}}
        quotes = db.db.history.find(query)
        if quotes.count() > 0:
            return True

    names = []

    users = db.db.users.find()
    for user in users:
        names.append((user['nick'], user))
        #print "-----"
        #print user
        if 'nicks' in user:
            for r in user['nicks']:
                #print r
                for n in r['nicks']:
                    #print n
                    names.append((n, user))

    #print "Names Found!", names

    results = []

    def compare(search, result):
        if search == result:
            return MULT_EXACT
        if result[:len(search)] == search:
            return MULT_PART_FIRST
        else:
            return MULT_PART_OTHER

    for item in names:
        v = 0
        n = item[0]
        if name in n:
            #print name, "in", n
            v = compare(name, n)
        elif name.lower() in n.lower():
            #print name, "lower in", n
            v = compare(name.lower(), n.lower()) * MULT_CASE_WRONG
        if v > 0:
            results.append((item[1], v))

    if len(results) > 0:
        return sorted(results, key=itemgetter(1), reverse=True)
    else:
        return False
