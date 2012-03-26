import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response

class MyModule:
	zope.interface.implements(IModule)
	name=""
	description=""
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("keywords", self.function, self, "Name", "Description")
		intent.service.registerListener("keywords", self.function, self, "Name", "Description")


module = MyModule()