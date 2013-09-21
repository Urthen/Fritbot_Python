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
		},
		"install": {
			"keywords": "install module",
			"function": "install",
			"name": "Install Module",
			"description": "Installs available module, by ID as returned by 'list modules'"
		},
		"remove": {
			"keywords": "(remove|uninstall) module",
			"function": "remove",
			"name": "Remove Module",
			"description": "Removes available module, by ID as returned by 'list modules installed'"
		}
	}

	@response
	def list(self, bot, room, user, args):
		if len(args) > 0 and args[0] == "installed":
			available = ["%s - %s" % (mod['id'], mod['name']) for mod in moduleLoader.installed_modules]
		else:
			available = ["%s - %s" % (mod['id'], mod['name']) for mod in moduleLoader.available_modules]

		return '\n'.join(available)

	@response
	def install(self, bot, room, user, args):
		if len(args) < 1:
			return "Must specify a module to install!"

		try:
			moduleLoader.installModule(args[0])
		except KeyError:
			return "Module %s not available!" % args[0]

		return "Module %s installed!" % args[0]

	@response
	def remove(self, bot, room, user, args):
		if len(args) < 1:
			return "Must specify a module to remove!"

		try:
			moduleLoader.uninstallModule(args[1])
		except KeyError:
			return "Module %s not installed, nothing to do." % args[1]
		except ValueError:
			return "Module %s cannot be uninstalled." % args[1]
		else:
			return "Module %s uninstalled!" % args[1]

module = ModuleCommandsModule
