from fb.modulecontrol import moduleLoader
from fb.modules.base import Module, response

def renderModule(module, prefix = ""):
	out = []

	for command in module['commands'].values():
		out.append(prefix + "\- {0}: {1} - {2}".format(command['name'], command['keywords'], command['description']))

	for child in module['children']:
		out.extend(renderModule(child, prefix + "| "))

	if len(out):
		out.insert(0, prefix + "\n" + prefix + "+ {0} - {1} ({2})".format(module['name'], module['description'], module['author']))

	return out


class HelpModule(Module):

	uid="chat_core.help"
	name="Help Functions"
	description="Functions to document what commands the bot currently has available."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	commands = {
		"help": {
			"keywords": ["help", "manual"],
			"function": "help",
			"name": "Help",
			"description": "List all available commands"
		}
	}

	listeners = {
		"help": {
			"keywords": ["man fritbot"],
			"function": "help",
			"name": "Help",
			"description": "List all available commands"
		}
	}

	def help(self, bot, room, user, args):
		out = ["Available Functions:"]

		for module in moduleLoader.installed_modules:
			out.extend(renderModule(module))

		user.send('\n'.join(out))
		return True


module = HelpModule