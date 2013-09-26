import fb.intent as intent
from fb.modules.base import Module, response

class SubModuleOne(Module):

	uid="supermodule_example.subone"
	name="SubModuleOne"
	description="Test Submodule One Yeah"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	commands = {
		"test": {
			"keywords": "test1",
			"function": "function",
			"name": "Test 1",
			"description": "First Test Function"
		}
	}

	@response
	def function(self, bot, room, user, args):
		return "Test One is yes!"

module = SubModuleOne