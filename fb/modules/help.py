import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response

class HelpModule:
	zope.interface.implements(IModule)

	name="Help Functions"
	description="Functions to document what commands the bot currently has available."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand(["help", "manual"], self.help, self, "Help", "List all available commands.")
		intent.service.registerListener(["man fritbot"], self.help, self, "Help", "List all available commands")

	def help(self, bot, room, user, args):
		out = ["Available commands:"]
		modules = {}

		for command in intent.service._commands:
			tagline = "{0} - {1} ({2})".format(command['module'].name, command['module'].description, command['module'].author)

			if tagline not in modules:
				modules[tagline] = []

			modules[tagline].append("* {0}: {1} - {2}".format(command['name'], command['originals'], command['description']))

		for module in sorted(modules.keys()):
			out.append(module)
			commands = sorted(modules[module])
			for command in commands:
				out.append(command)
			out.append("")

		user.send('\n'.join(out))
		return True


module = HelpModule()