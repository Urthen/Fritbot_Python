import fb.intent as intent
from fb.modules.base import FritbotModule, response

class HelloWorldModule(FritbotModule):

	name="Hello World"
	description="Simple static functions for demonstration purposes."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("say (hello)|(hi)", self.sayHello, self, "Say Hello", "Says hello to the user.")
		intent.service.registerListener("(hello)|(hi) fritbot", self.sayHello, self, "Greet Fritbot", "Someone said hello to the bot.")

	@response
	def sayHello(self, bot, room, user, args):
		return "Hello, " + user['nick']

module = HelloWorldModule()