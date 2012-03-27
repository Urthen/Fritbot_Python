import zope.interface

from fb.modules.base import IModule
from fb.modules.facts import api, commands

class FactsModule:
	zope.interface.implements(IModule)

	name="Facts"
	description="Responds to other users' chats with super A+ userful factoids."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		api.module.register(self)
		commands.module.register(self)
				
children = [api, commands]
module = FactsModule()
