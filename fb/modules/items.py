import random, datetime, re

import fb.intent as intent
from fb.modules.base import FritbotModule, response

from fb.db import db

class ItemsModule(FritbotModule):

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

		return "Thanks for {0}!".format(outitem)

	@response
	def commanddestroy(self, bot, room, user, args):
		item = ' '.join(args)

		if db.items.find_one({'name': item}) is not None:
			db.items.remove({'name': item})
			return "I've completely erased {0} from existance!".format(item)
		else:
			return "I don't know about {0} in the first place...".format(item)

	@response
	def commandinventory(self, bot, room, user, args):
		inventory = self.getItems(owned=True)
		
		if not inventory:
			return "My inventory seems to be empty!"
		elif len(inventory) == 1:
			return "I have {0}.".format(inventory[0]['name'])
		else:
			inventory[-1] = "and " + inventory[-1]  
			return "I've got {0}.".format(', '.join(inventory))

	@response
	def commanddrop(self, bot, room, user, args):
		name = ' '.join(args)
		if name == 'something':
			name = self.getPosesssion()
		item = self.giveItem(name)
		if item is not None:
			return "I no longer have {0}!".format(item['name'])
		else:
			return "I'm not sure what that is..."
		
	def getItems(self, owned=None):
		query = {}
		if owned is not None:
			query = {'owned': owned}
		out = [item['name'] for item in db.items.find(query)]
		if out:
			return out
		else:
			return ['something']

	def getSomething(self):
		return random.choice(self.getItems())
	def getPosesssion(self):
		return random.choice(self.getItems(owned=True))
	def getNotCarried(self):
		return random.choice(self.getItems(owned=False))

	def giveItem(self, item=None):
		if item is None:
			item = random.choice(self.getItems(owned=True))
		else:
			item = db.items.find_one({'name': {'$regex': item, '$options': 'i'}, 'owned': True})['name']
			if item is None:
				return None


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