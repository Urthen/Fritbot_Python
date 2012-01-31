import fb.intent as intent
from fb.modules.base import FritbotModule, response

class MyModule(FritbotModule):

	name=""
	description=""
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("keywords", self.function, self, "Name", "Description")
		intent.service.registerListener("keywords", self.function, self, "Name", "Description")


module = MyModule()