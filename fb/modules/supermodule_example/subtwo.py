import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response

class SubModuleTwo:
	zope.interface.implements(IModule)
	name="SubModuleTwo"
	description="Testing !!! Two!! "
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self, parent):
		intent.service.registerCommand("test2", self.function, parent, "Test 2", "Second test function")

	@response
	def function(self, bot, room, user, args):
		return "Test Two success!"

module = SubModuleTwo