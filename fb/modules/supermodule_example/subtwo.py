import fb.intent as intent
from fb.modules.base import Module, response

class SubModuleTwo:

	uid="supermodule_example.subtwo"
	name="SubModuleTwo"
	description="Testing !!! Two!! "
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	commands = {
		"test": {
			"keywords": "test2",
			"function": "function",
			"name": "Test 2",
			"description": "Second Test Function"
		}
	}

	@response
	def function(self, bot, room, user, args):
		return "Test Two success!"

module = SubModuleTwo