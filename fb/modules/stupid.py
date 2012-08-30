import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response

class StupidModule:
	zope.interface.implements(IModule)

	name="Stupid"
	description="This is stupid."
	author="Tom Grochowicz (tom.grochowicz@bazaarvoice.com)"

	def register(self):

		intent.service.registerListener(r"\bex\w*\b", self.sex, self, "Extra sex", "Someone said something sexy.")

	@response
	def sex(self, bot, room, user, args):
		if not room.allowed('stupid'):
			return False

		keyword = args.group(0)
		return keyword.capitalize() +"? More like S"+keyword.upper()+"!"


module = StupidModule()