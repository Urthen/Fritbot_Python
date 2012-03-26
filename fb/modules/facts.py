import re, random

import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response
from fb.db import db
from fb.api.core import api
from fb.api.util import returnjson

try:
	from fb.modules.items import module as itemmodule
except ImportError:
	raise ImportError, "Can't find the items module, which is required for the facts module!"

class FactsModule:
	zope.interface.implements(IModule)


	name="Facts"
	description="Responds to other users' chats with super A+ userful factoids."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		apimodule = api.registerModule('facts')
		apimodule.putSimpleChild('list', self.apilist)

		intent.service.registerListener("^.*$", self.checkfacts, self, "Fact Listener", "Listen for fact triggers and respond as appropriate")
		self.refresh()

	def refresh(self):
		triggers = db.facts.find({}, {'triggers': 1})
		self.trigger_cache = {}

		for triggerset in triggers:
			for trigger in triggerset['triggers']:
				if trigger not in self.trigger_cache:
					self.trigger_cache[trigger] = {'rex': re.compile(trigger), 'facts': [], 'triggered': None}
				
				if triggerset['_id'] not in self.trigger_cache[trigger]['facts']:
					self.trigger_cache[trigger]['facts'].append(triggerset['_id'])

	def checkfacts(self, bot, room, user, args):
		body = args.group()

		response = None
		count = None

		for trigger in self.trigger_cache.values():
			check = trigger['rex'].search(body)
			if check is not None:
				for factid in trigger['facts']:
					fact = db.facts.find_one({'_id': factid})

					if count is None or fact['count'] < count:
						response = fact
						count = fact['count']

		if response is None:
			return None

		response['count'] = response['count'] + 1
		db.facts.update({'_id': response['_id']}, response)

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
				reply = reply.replace('$someone', random.choice(room.roster), 1)

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

	@returnjson
	def apilist(self, request):
		factlist = []
		for fact in db.facts.find({}, {'_id': 0}):
			fact['created'] = str(fact['created'])
			for factoid in fact['factoids']:
				factoid['created'] = str(factoid['created'])

			factlist.append(fact)

		return {'facts': factlist}
				

module = FactsModule()