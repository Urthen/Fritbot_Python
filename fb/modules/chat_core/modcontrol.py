import fb.intent as intent
from fb.modules.base import Module, response
from fb.modulecontrol import moduleLoader

class ModuleCommandsModule(Module):
	
	uid="chat_core.modcontrol"
	name="Module Control Commands"
	description="Chat commands to alter loaded modules"
	author="Michael Pratt (michael.pratt@bazaaarvoice.com)"

	commands = {
		"list": {
			"keywords": "list modules",
			"function": "list",
			"name": "List Modules",
			"description": "List all available modules. To limit to only installed & active modules, use 'list modules installed'"
		}
	}

	@response
	def list(self, bot, room, user, args):
		if len(args) > 0 and args[0] == "installed":
			available = ["%s - %s" % (mod['id'], mod['name']) for mod in moduleLoader.installed_modules]
		else:
			available = ["%s - %s" % (mod['id'], mod['name']) for mod in moduleLoader.available_modules]

		return '\n'.join(available)

module = ModuleCommandsModule
