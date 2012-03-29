import re, random, datetime

import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response
from fb.db import db

min_repeat = 300
max_repeat = 600

try:
	from fb.modules.items import module as itemmodule
except ImportError:
	raise ImportError, "Can't find the items module, which is required for the facts commands module!"

class FactsCommandModule:
	zope.interface.implements(IModule)

	name="Facts Command Module"
	description="Listener to respond to other users' chats with super A+ userful factoids."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self, parent):
		intent.service.registerListener("^.*$", self.checkfacts, parent, "Fact Listener", "Listen for fact triggers and respond as appropriate")
		self.refresh()

	def refresh(self):
		triggers = db.facts.find({'$or': [{'removed': False}, {'removed': {'$exists': False}}]}, {'triggers': 1})
		self.trigger_cache = {}

		for triggerset in triggers:
			for trigger in triggerset['triggers']:
				if trigger not in self.trigger_cache:
					self.trigger_cache[trigger] = {'rex': re.compile(trigger), 'original': trigger, 'facts': [], 'triggered': None}
				
				if triggerset['_id'] not in self.trigger_cache[trigger]['facts']:
					self.trigger_cache[trigger]['facts'].append(triggerset['_id'])

	def checkfacts(self, bot, room, user, args):
		if room is not None and not room.allowed('facts'):
			return False
			
		body = args.group()

		response = None
		triggered = None
		count = None

		for trigger in self.trigger_cache.values():
			check = trigger['rex'].search(body)
			if check is not None:
				for factid in trigger['facts']:
					fact = db.facts.find_one({'_id': factid})
					match = trigger['rex'].match(body)
					if trigger['triggered'] is not None and (match is None or match.group() != body):
						delta = (datetime.datetime.now() - trigger['triggered']).total_seconds()
						if delta < min_repeat:
							print "Would have spouted fact {0} but was too soon (absolute)".format(str(fact['triggers']))
							continue
						elif (delta - min_repeat) > random.randrange(1, max_repeat - min_repeat):
							print "Would have spouted fact {0} but was too soon (random)".format(str(fact['triggers']))
							continue

					if count is None or fact['count'] < count:
						response = fact
						triggered = trigger
						count = fact['count']

		if response is None:
			return False

		response['count'] = response['count'] + 1
		db.facts.update({'_id': response['_id']}, response)
		triggered['triggered'] = datetime.datetime.now()

		reply = random.choice(response['factoids'])['reply']

		try:
			what = args.group('what')
		except IndexError:
			what = itemmodule.getSomething()

		reply = reply.replace('$who', user['nick']).replace('$what', what)

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
		else:
			user.send(reply, delay=True)
			
		return True


module = FactsCommandModule()
