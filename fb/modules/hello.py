import fb.intent as intent
from fb.modules.base import Module, response

class HelloWorldModule(Module):

	uid="hello"
	name="Hello World"
	description="Simple static functions for demonstration purposes."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	commands = {
		"hello": {
			"keywords": "say ((hello)|(hi))",
			"function": "sayHello",
			"name": "Say Hello",
			"description": "Says Hello to the user"
		}
	}

	listeners = {
		"hello": {
			"keywords": "((hello)|(hi)) fritbot",
			"function": "sayHello",
			"name": "Greet Fritbot",
			"description": "Someone said hello to the bot"
		}
	}

	@response
	def sayHello(self, bot, room, user, args):
		return "Hello, " + user['nick']

module = HelloWorldModule
