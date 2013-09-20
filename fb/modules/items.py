import random, datetime, re

import zope.interface

from twisted.internet import reactor

import fb.intent as intent
from fb.modules.base import IModule, response

from fb.db import db

class ItemsModule:
	zope.interface.implements(IModule)

	name="Items & Inventory"
	description="Handles a fictitious items & inventory system, allowing you to give and take items from the bot."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand(["have", "take"], self.commandgive, self, "Give Item", "Gives an item to fritbot, as in 'Fritbot, have a banana'")
		intent.service.registerCommand(["backpack", "inventory"], self.commandinventory, self, "List Inventory", "Replies with all items currently in the bot's backpack")
		intent.service.registerCommand(["drop", "give me"], self.commanddrop, self, "Drop Item", "Removes an item from the bot's inventory, but it continues to exist. Works with subsets, example, 'drop apple' will drop 'an apple'.")
		intent.service.registerCommand(["destroy"], self.commanddestroy, self, "Destory Item", "Named item will be wiped from existance, never to return again until you give it back. Does NOT work with subsets, must be exact name.")

	@response
	def commandgive(self, bot, room, user, args):
		item = ' '.join(args)
		if item == 'something':
			item = self.getNotCarried()
		outitem = re.sub(r'\bmy\b', 'your', item)
		item = re.sub(r'\bmy\b', user['nick'] + "'s", item)

		self.takeItem(item, user)

		inventory = self.getItems(owned=True)
		if len(inventory) > 10:
			kill = random.choice(range(5))
			if kill == 0:
				reactor.callLater(2.0, room.send, "Here, %s, take %s. I don't want it anymore." % (random.choice(room.roster.values())['nick'], self.giveItem()))
			elif kill == 1:
				reactor.callLater(2.0, room.send, "Whoops... I dropped %s down the stairs, though, so, I don't have that anymore." % self.giveItem())
			elif kill == 2:
				reactor.callLater(2.0, room.send, "/me smashes %s into %s, breaking them both into bits. Confetti for everyone!" % (self.giveItem(), self.giveItem()))
			elif kill == 3:
				reactor.callLater(2.0, room.send, "I may have accidentally... er... lost %s and %s." % (self.giveItem(), self.giveItem()))
			elif kill == 4:
				reactor.callLater(2.0, room.send, "... coincidentally, I set %s on fire." % self.giveItem())

		return "Thanks for {0}!".format(outitem)

	@response
	def commanddestroy(self, bot, room, user, args):
		item = ' '.join(args)

		if db.items.find_one({'name': item}) is not None:
			db.items.remove({'name': item})
			return "{1} has completely erased {0} from existance!".format(item, user['nick'])
		else:
			return "I don't know about {0} in the first place...".format(item)

	@response
	def commandinventory(self, bot, room, user, args):
		inventory = self.getItems(owned=True)
		
		if not inventory:
			return "My inventory seems to be empty!"
		elif len(inventory) == 1:
			return "I have {0}.".format(inventory[0])
		else:
			inventory[-1] = "and " + inventory[-1]  
			return "I've got {0}.".format(', '.join(inventory))

	@response
	def commanddrop(self, bot, room, user, args):
		if not self.getItems(owned=True):
			return "I don't have anything to give you, {0}!".format(user['nick'])
		name = ' '.join(args)
		if name == 'something':
			name = self.getPosesssion()
		item = self.giveItem(name)
		if item is not None:
			return "Ok, I no longer have {0}!".format(item)
		else:
			return "I don't have {0} to give you!".format(name)
		
	def getItems(self, owned=None):
		query = {}
		if owned is not None:
			query = {'owned': owned}
		out = [item['name'] for item in db.items.find(query)]
		return out

	def getSomething(self):
		out = random.choice(self.getItems())
		if not out:
			out = 'something'
		return out

	def getPosesssion(self):
		out = random.choice(self.getItems(owned=True))
		if not out:
			out = 'something'
		return out

	def getNotCarried(self):
		out = random.choice(self.getItems(owned=False))
		if not out:
			out = 'something'
		return out

	def giveItem(self, item=None):
		if item is None:
			item = random.choice(self.getItems(owned=True))
		else:
			item = db.items.find_one({'name': {'$regex': item, '$options': 'i'}, 'owned': True})
			if item is None:
				return None
			else:
				item = item['name']


		db.items.update({'name': item}, {'$set': {'owned': False}})
		return item

	def takeItem(self, item=None, author=None):
		if item is None:
			item = random.choice(self.getItems(owned=False))

		if db.items.find_one({'name': item}) is not None:
			db.items.update({'name': item}, {'$set': {'owned': True}})
			return item
		else:
			if author is not None:
				doc = {
					'name': item,
					'owned': True,
					'author': author['_id'],
					'created': datetime.datetime.now()
				}
				db.items.insert(doc)
				return item

module = ItemsModule()
