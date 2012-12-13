from pymongo import Connection, errors as PyMongoErrors
import cmd

connection = Connection()
db = connection["fritbot"]

class UserResult(object):

	valid = False
	nick = None
	resource = None
	uid = ""
	nicks = []

	def __init__(self, result):
		if result is None:
			return

		self.nick = result['nick']
		self.resource = result['resource']
		self.uid = result['_id']
		self.valid = True

	def __str__(self):
		return "{0} - {1} ({2}) {3}".format(self.nick, self.resource, self.uid, str(self.nicks))

class RepairTool(cmd.Cmd):
	"""Fritbot command line repair tool. Yeah!"""

	nicks = {}
	state = "EMPTY"
	prompt = "(Fritbot) "

	def do_nickscan(self, line):
		"""Scans for abandonded nicknames (those without ID)"""
		print "Scanning"
		self.nicks = {}
		results = db.history.find({'user.id': {'$exists': False}}, {'user.nick': 1})
		for result in results:
			nick = result['user']['nick']
			self.nicks[nick] = None
		print "Detected %i invalid users in the history" % len(self.nicks)
		self.state = "SCANNED_NICKS"

	def do_autonick(self, line):
		"""Attempts to automatically fix scanned nicknames"""

		if self.state == "EMPTY":
			print "Scan first with nickscan!"
			return

		limit = len(self.nicks)
		try:
			limit = int(line)
		except:
			pass

		self.state = "REPAIRING_NICKS"

		i = 0
		repaired = 0

		print "Attempting autorepair..."
		for nick in self.nicks.keys()[0:limit]:
			if (i % 10 == 0):
				print "%i/%i" % (i, limit)
			i += 1
			nickresult = db.history.find_one({'user.id': {'$exists': True}, 'user.nick': {'$regex': '^' + nick + '$', '$options': 'i'}})
			if nickresult:
				user = UserResult(db.users.find_one({'_id': nickresult['user']['id']}))
				if user.nick.upper() == nick.upper():
					self.nicks[nick] = user
					repaired += 1
				else:
					user = UserResult(db.users.find_one({'nick': {'$regex': '^' + nick + '$', '$options': 'i'}}))
					if user.valid:
						self.nicks[nick] = user
						repaired += 1

		print "%i/%i repairable" % (repaired, len(self.nicks))

	def do_status(self, line):
		"""Lists valid and invalid nicknames."""

		def listNicks():
			repaired = {key: self.nicks[key] for key in self.nicks if self.nicks[key] is not None}

			print "============= Nicks: %i repairable =====" % len(repaired)
			for nick in repaired.keys():
				print "%s => %s" % (nick, repaired[nick].nick)

			unrepaired = {key: self.nicks[key] for key in self.nicks if self.nicks[key] is None}

			print "============= %i outstanding ==========" % len(unrepaired)

			for nick in unrepaired:
				print nick

		if self.state == "EMPTY":
			print "Unscanned."
			return
		elif self.state == "SCANNED_NICKS":
			print "Scanned nicknames, ready to repair."
			listNicks()
		elif self.state == "REPAIRING_NICKS":
			print "Repairing nicknames"
			listNicks()

	def do_nickapply(self, line):

		print "Applying changes..."
		for nick, user in self.nicks.items():
			if user is None:
				continue

			db.history.update({'user.nick': nick, 'user.id': {'$exists': False}}, {'$set': {'user.id': user.uid}}, multi=True)

	def do_find_nick(self, line):
		userresults = db.users.find({'$or': [{'nick': line}, {'nicks.nicks': line}]});

		if userresults.count() > 0:
			for result in userresults:
				print UserResult(result)

		else:
			print "No results found"



	def do_EOF(self, line):
		return True;


if __name__ == '__main__':
	RepairTool().cmdloop();
