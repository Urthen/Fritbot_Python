'''
This is not a real module, of course - use this boilerplate to copy/paste into your own new modules and get started almost immediately!
'''

import fb.intent as intent
from fb.modules.base import Module, response

class MyModule(Module):
	
	uid=""
	name=""
	description=""
	author="Your Name (your.email@example.com)"

	children = []

	listeners = {
		"listener": {
			keywords: "keywords",
			function: "function",
			name: "Name",
			description: "Description"
		}
	}

	commands = {
		"command": {
			keywords: "keywords",
			function: "function",
			name: "Name",
			description: "Description"
		}
	}

	apis = {
		"path": SomeModule
	}

	def register(self):
		intent.service.registerCommand("keywords", self.function, self, "Name", "Description")
		intent.service.registerListener("keywords", self.function, self, "Name", "Description")

module = MyModule