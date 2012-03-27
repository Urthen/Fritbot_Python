import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response

class SubModuleOne:
	zope.interface.implements(IModule)
	name="SubModuleOne"
	description="Test Submodule One Yeah"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self, parent):
		intent.service.registerCommand("test1", self.function, parent, "Test 1", "First test function")

	@response
	def function(self, bot, room, user, args):
		return "Test One is yes!"

module = SubModuleOne()