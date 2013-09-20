'''
This is not a real module, of course - use this boilerplate to copy/paste into your own new modules and get started almost immediately!
'''

import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response

class MyModule:
	zope.interface.implements(IModule)
	name=""
	description=""
	author="Your Name (your.email@example.com)"

	def register(self):
		intent.service.registerCommand("keywords", self.function, self, "Name", "Description")
		intent.service.registerListener("keywords", self.function, self, "Name", "Description")


module = MyModule()