import random, re, datetime
from operator import itemgetter

import zope.interface

from pymongo import ASCENDING, DESCENDING

from fb.db import db

import fb.intent as intent
from fb.modules.base import IModule, response

MULT_EXACT = 1.0
MULT_CASE_WRONG = 0.9
MULT_PART_WORD = 0.8
MULT_PART_FIRST = 0.6
MULT_PART_OTHER = 0.4

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

	names = []

	users = db.db.users.find()
	for user in users:
		names.append((user['nick'], user))
		names.append((user['resource'], user))

	if room is not None:
		for nick, user in room.roster.items():
			names.append((nick, user.info))

	#print names

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
			tuser = inRoster(args[0], room, special="quotes")
			if tuser:
				user = args[0]
				args = args[1:]
		else:
			args = args[1:]

		if len(args) > 0:
			segment = ' '.join(args)

	return user, segment, min, max

def sayQuotes(room, user, nick, segment, min=1, max=1):
	if max < min:
		max = min

	if max > 10:
		return "Too many, jerkwad!"

	query = {'remembered': {'$exists': True}}
	if nick is not None:
		nickq = {'user.nick': {'$regex': nick, '$options': 'i'}}
		ids = inRoster(nick)
		if ids:
			idq = {'user.id': {'$in': map(lambda x: x[0]['_id'], ids)}}
			query['$or'] = [nickq, idq]
		else:
			query.update(nickq)

	if segment is not None:
		query['body'] = {'$regex': segment, '$options': 'i'}  

	quotes = db.db.history.find(query)

	msg = None
	if quotes.count() == 0:
		msg = "I can't find any quotes"
		if nick is not None:
			msg += " for user {0}".format(nick)

		if segment is not None:
			msg += " with string '{0}'".format(segment)
	else:        
		quotes = getSubset(quotes, min, max)
		lines = []
		for quote in quotes:
			lines.append(u"<{0}>: {1}".format(quote['user']['nick'], quote['body']))
		msg = '\n'.join(lines)

	return msg

class QuotesModule:
	zope.interface.implements(IModule)

	name="Quotes"
	description="Remember and recite quotes users have said in chat rooms."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("quote", self.quote, self, "Name", "Recalls a random quote, optionally from a specific person and/or containing specific text.")
		intent.service.registerCommand("quotemash", self.quotemash, self, "Name", "Recalls 3-6 random quotes, optionally from a specific person or containing specific text.")
		intent.service.registerCommand("remember", self.remember, self, "Remember", "Remembers a quotation with 'remember \"nickname\" \"quote to remember\"'")

	@response
	def quote(self, bot, room, user, args):
		nick, segment, min, max = parseQuoteArgs(args, room)
		if min is None:
			min = 1
			max = 1

		return sayQuotes(room, user, nick, segment, min, max)

	@response
	def quotemash(self, bot, room, user, args):
		nick, segment, min, max = parseQuoteArgs(args, room)
		if min is None:
			min = 3
			max = 6

		return sayQuotes(room, user, nick, segment, min, max)

	@response
	def remember(self, bot, room, user, args):
		if room is None:
			return "Can't remember private conversations!"

		if len(args) == 0:
			return "Remember what, exactly?"

		tuser = inRoster(args[0], room)

		#print "tuser:", tuser
		if tuser and len(tuser) >= 1:
			text = " ".join(args[1:])

			for u in tuser:
				query = {"user.id": u[0]["_id"], "room": room.info["_id"], "body": {"$regex": text, '$options': 'i'}, 
					"command": False, 'date': {'$gt': datetime.datetime.now() - datetime.timedelta(hours=3)}}

				quote = db.db.history.find_one(query, sort=[("date", DESCENDING)])
				print "query:", query
				#print "quote:", quote

				if quote:
					if quote['user']['id'] == user['_id']:
						return "Sorry, {0}, but you can't quote yourself! Try saying someone funnier and maybe someone else will remember you.".format(user['nick'])
					if "remembered" in quote:
						return u"Sorry, {0}, I already knew about <{1}>: {2}".format(user["nick"], quote['user']["nick"], quote["body"])
					else:
						quote["remembered"] = {"user": user["_id"], "nick": user["nick"], "time": datetime.datetime.now()}
						db.db.history.save(quote)
						return u"Ok, {0}, remembering <{1}>: {2}".format(user["nick"], quote['user']['nick'], quote["body"])

			return "Sorry, {0}, I haven't heard anything like '{1}' by anyone named {2}.".format(user["nick"], text, args[0])

		elif not tuser:
			return "Hrm, the name {0} doesn't ring any bells.".format(args[0])
		else:
			return "Sorry, {0} isn't unique enough. Too many users matched!".format(args[0])

module = QuotesModule()
