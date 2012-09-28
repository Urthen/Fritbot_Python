from twisted.python import log
import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, require_auth, ratelimit, response

class StupidModule:
	zope.interface.implements(IModule)

	name="Stupid"
	description="This is stupid."
	author="Tom Grochowicz (tom.grochowicz@bazaarvoice.com)"

	def register(self):
		intent.service.registerListener(r"\bex\w*\b", self.sex, self, "Extra sex", "Someone said something sexy.")

	@ratelimit(30)
	@require_auth('stupid')
	@response	
	def sex(self, bot, room, user, args):
		keyword = args.group(0)
		return keyword.capitalize() +"? More like S"+keyword.upper()+"!"


module = StupidModule()