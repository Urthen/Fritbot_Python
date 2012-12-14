from operator import itemgetter

from fb.db import db

MULT_EXACT = 1.0
MULT_CASE_WRONG = 0.9
MULT_PART_WORD = 0.8
MULT_PART_FIRST = 0.6
MULT_PART_OTHER = 0.4

def getUser(name, room=None, special=None):

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