import zope.interface

from fb.modules.base import IModule
from fb.modules.chat_core import core, help, security

class ChatCoreModule:
	zope.interface.implements(IModule)

	name="Chat Core"
	description="Core Chat Modules"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		core.module.register(self)
		help.module.register(self)
		security.module.register(self)
				
children = [core, help, security]
module = ChatCoreModule()
