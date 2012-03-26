import fb.intent as intent
from fb.modules.base import FritbotModule, response

class HelpModule(FritbotModule):

	name="Help Functions"
	description="Functions to document what commands the bot currently has available."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("help", self.help, self, "Help", "List all available commands.")

	def help(self, bot, room, user, args):
		out = ["Available commands:"]
		modules = {}

		for command in intent.service._commands:
			tagline = "{0} - {1} ({2})".format(command['module'].name, command['module'].description, command['module'].author)

			if tagline not in modules:
				modules[tagline] = []

			modules[tagline].append("* {0}: {1} - {2}".format(command['name'], command['originals'], command['description']))

		for module in modules:
			out.append(module)
			for command in modules[module]:
				out.append(command)
			out.append("")

		user.send('\n'.join(out))
		return True


module = HelpModule()