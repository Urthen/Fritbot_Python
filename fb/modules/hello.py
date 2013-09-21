import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response

class HelloWorldModule:
	zope.interface.implements(IModule)

	name="Hello World"
	description="Simple static functions for demonstration purposes."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand(
			keywords = "say ((hello)|(hi))", 
			function = self.sayHello, 
			module = self, 
			name = "Say Hello", 
			description = "Says hello to the user.")
		intent.service.registerListener("((hello)|(hi)) fritbot", self.sayHello, self, "Greet Fritbot", "Someone said hello to the bot.")

	@response
	def sayHello(self, bot, room, user, args):
		return "Hello, " + user['nick']

module = HelloWorldModule
