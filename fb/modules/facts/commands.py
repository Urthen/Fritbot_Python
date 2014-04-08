import re, random, datetime, urllib

from twisted.python import log

import fb.intent as intent
from fb.modules.base import Module, response, room_only
from fb.db import db

short_time = datetime.timedelta(minutes=2)
short_count = 3
min_repeat = datetime.timedelta(minutes=5)
max_repeat = datetime.timedelta(minutes=15)

try:
	from fb.modules.items import module as itemmodule_class
except ImportError:
	raise ImportError, "Can't find the items module, which is required for the facts commands module!"

itemmodule = itemmodule_class()

class FactsCommandModule(Module):

	uid="facts.commands"
	name="Facts Command Module"
	description="Listener to respond to other users' chats with super A+ userful factoids."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	listeners = {
		"message": {
			"keywords": "^.+$",
			"function": "checkfacts",
			"name": "Fact Listener",
			"description": "Listen for fact triggers and respond as appropriate"
		}
	}

	commands = {
		"wtf": {
			"keywords": "what.*was that",
			"function": "describeFact",
			"name": "What was that",
			"description": "Returns what the last fact spouted in the room was"
		},
		"learn": {
			"keywords": "learn",
			"function": "learnFact",
			"name": "Learn Fact",
			"description": "Learns a fact response. Use: fb learn 'hello fritbot' 'hello $who'"
		},
		"forget": {
			"keywords": "forget that",
			"function": "forgetFact",
			"name": "Forget Fact",
			"description": "Forgets the most recent fact response"
		}
	}

	def __init__(self):
		Module.__init__(self)
		self.triggered = {}
		self.refresh()

	def refresh(self):
		triggers = db.facts.find({'$or': [{'removed': False}, {'removed': {'$exists': False}}]}, {'triggers': 1})
		self.trigger_cache = {}

		for triggerset in triggers:
			for trigger in triggerset['triggers']:
				if trigger not in self.trigger_cache:
					try:
						self.trigger_cache[trigger] = {'rex': re.compile(trigger), 'original': trigger, 'facts': [], 'triggered': None}
					except Exception as e:
						print "Error compiling fact:", trigger
						print e			
						continue

				if triggerset['_id'] not in self.trigger_cache[trigger]['facts']:
					self.trigger_cache[trigger]['facts'].append(triggerset['_id'])

	def checkfacts(self, bot, room, user, args):
		if room is not None and not room.allowed('facts'):
			return False
			
		body = args.group()

		response = None
		count = None

		shorted = room is not None and room["_id"] in self.triggered and (self.triggered[room["_id"]]['count'] > short_count and datetime.datetime.now() - self.triggered[room["_id"]]['time'] < min_repeat)

		for trigger in self.trigger_cache.values():
			check = trigger['rex'].search(body)
			if check is not None:
				for factid in trigger['facts']:
					fact = db.facts.find_one({'_id': factid})
					match = trigger['rex'].match(body)
					if trigger['triggered'] is not None and (match is None or match.group() != body):
						if shorted:
							continue
						delta = datetime.datetime.now() - trigger['triggered']
						if delta < min_repeat:
							print "Would have spouted fact {0} but was too soon (absolute)".format(str(fact['triggers']))
							continue
						elif (delta - min_repeat) < datetime.timedelta(seconds=random.randrange(1, (max_repeat - min_repeat).seconds)):
							print "Would have spouted fact {0} but was too soon (random)".format(str(fact['triggers']))
							continue

					if count is None or fact['count'] < count:
						response = fact
						triggered = trigger
						count = fact['count']

		if response is None:
			return False

		if room is not None and match is not None and match.group() != body:
			if room["_id"] not in self.triggered:
				self.triggered[room["_id"]] = {'count': 1, 'time': datetime.datetime.now()}
			else:
				if datetime.datetime.now() - self.triggered[room["_id"]]['time'] < short_time:
					self.triggered[room["_id"]] = {'count': self.triggered[room["_id"]]['count'] + 1, 'time': datetime.datetime.now()}
				else:
					self.triggered[room["_id"]] = {'count': 1, 'time': datetime.datetime.now()}


		response['count'] = response['count'] + 1
		response['triggered'] = datetime.datetime.now()
		triggered['triggered'] = response['triggered']
		db.facts.update({'_id': response['_id']}, response)

		factoid = random.choice(response['factoids'])


		what = itemmodule.getSomething()
		if match:
			try:
				what = match.group(1)
			except IndexError:
				pass

		reply = factoid["reply"].replace('$who', user['nick']).replace('$what', what).replace('$query', urllib.quote(what))

		while '$something' in reply:
			reply = reply.replace('$something', itemmodule.getSomething(), 1)
		
		while '$someone' in reply:
			if room is None:
				reply = reply.replace('$someone', "someone", 1)
			else:
				reply = reply.replace('$someone', random.choice(room.roster.values())['nick'], 1)

		while '$inventory' in reply:
			reply = reply.replace('$inventory', itemmodule.getPossession(), 1)

		while '$takeitem' in reply:
			reply = reply.replace('$takeitem', itemmodule.takeItem(), 1)

		while '$giveitem' in reply:
			reply = reply.replace('$giveitem', itemmodule.giveItem(), 1)

		if room is not None:
			room.send(reply, delay=True)
			room["factSpouted"] = {"fact": response, "trigger": triggered["original"], "factoid": factoid}
			room.save()

			if room["_id"] in self.triggered and self.triggered[room["_id"]]['count'] > 3:
				room.send("/me sparks and sputters. He's shorted out!", 5)
				print "shorted out until " + str(self.triggered[room["_id"]]['time'] + min_repeat)
		else:
			user.send(reply, delay=True)

			
		return True

	@room_only
	@response
	def describeFact(self, bot, room, user, args):
		if "factSpouted" in room.info:
			return "{0}: Triggered by '{1}', authored by {2}, {3}".format(room["factSpouted"]["factoid"]["reply"], room["factSpouted"]["trigger"], room["factSpouted"]["factoid"]["author"], room["factSpouted"]["factoid"]["created"])
		else:
			return "I haven't triggered anything here recently!"

	@response
	def learnFact(self, bot, room, user, args):
		if len(args) != 2:
			return "I'm expecting two arguments with quotes around them, for example, fb learn 'facts' 'facts are easy to teach'"

		trigger = args[0]
		factoid = args[1]

		if len(trigger) < 4:
			return "Trigger word must be longer than that, jerkwad."

		fact = db.facts.find_one({"triggers": trigger})

		if fact is not None:
			fact["factoids"].append({"reply": factoid, "author": user["nick"], "authorid": user["_id"], "created": datetime.datetime.now()})
			if "removed" in fact:
				del fact["removed"]
			db.facts.update({"_id": fact["_id"]}, fact)
		else:
			fact = {
				"created": datetime.datetime.now(),
				"count": 0,
				"triggers": [trigger],
				"factoids": [{
					"reply": factoid,
					"created": datetime.datetime.now(),
					"author": user["nick"],
					"authorid": user["_id"]
				}]
			}
			db.facts.insert(fact)
			self.refresh()

		return "Fact learned successfully!"

	@room_only
	@response
	def forgetFact(self, bot, room, user, args):
		if "factSpouted" in room.info:
		 	fact = room["factSpouted"]["fact"]
		 	factoid = room["factSpouted"]["factoid"]
		 	try:
		 		fact["factoids"].remove(factoid)
		 	except ValueError:
		 		del room.info["factSpouted"]
				room.save()
		 		return "Looks like that was already removed somehow..."

		 	if len(fact["factoids"]) == 0:
		 		fact["removed"] = user["_id"]
		 	
		 	db.facts.update({"_id": fact["_id"]}, fact)
			del room.info["factSpouted"]
			room.save()
			self.refresh()

		 	return "{0} factoid removed!".format(factoid["reply"])
		else:
			return "Hey, I didn't say anything yet."

module = FactsCommandModule
