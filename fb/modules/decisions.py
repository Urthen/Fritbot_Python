import random
from twisted.python import log
import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response

class DecisionsModule:
	zope.interface.implements(IModule)

	name="Decisions"
	description="Why make decisions when you can have a robot make them for you?"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("choose", self.choose, self, "Choice", "Decide between multiple choices. If a choice is multiple words, use quotes.")

	@response	
	def choose(self, bot, room, user, args):
		#Strip 'or'
		args = [arg for arg in args if arg != 'or']

		if len(args) < 2:
			return "{0}, I can't make a decision on just one thing!".format(user['nick'])

		#Strip question marks
		if args[-1][-1] == '?':
			args[-1] = args[-1][:-1]

		if random.random() > 0.15:
			choice = args[random.randrange(len(args))]
		else:
			if len(args) == 2:
				choice = "Both!"
			else:
				choice = "All of the above!"
		return "{0}: {1}".format(user['nick'], choice)

module = DecisionsModule()