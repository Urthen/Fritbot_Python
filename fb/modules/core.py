import fb.intent as intent
import fb.modules.base as base

class CoreCommandsModule(base.FritbotModule):
	name="Core Commands"
	description="Core Fritbot Commands, minimum functionality."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("reload modules", self.reloadModules, self, "Reload Modules", "(admin) Reload installed modules")
		intent.service.registerCommand("allow", self.allow, self, "Allow", "(admin) Assigns an authorization to the current room")
		intent.service.registerCommand("disallow", self.disallow, self, "Disallow", "(admin) Unassigns an authorization to the current room")
		intent.service.registerCommand("auths", self.auths, self, "Authorizations", "Lists current authorizations for the current room")
	
	@base.admin
	def reloadModules(self, bot, room, user, args):

		try:
			intent.service.loadModules()
		except:
			user.send("Modules did not reload successfully, check the error log.")
			raise

		user.send("Modules loaded successfully!")
		return True

	@base.admin
	@base.room_only
	@base.response
	def allow(self, bot, room, user, args):
		if len(args) < 1:
			return u"Must specify a permission..."
		else:
			auths = set(room["auths"]) | set(args)
			room["auths"] = list(auths)
			room.save()

			return u"Ok, allowing the following authorizations: {0}".format(repr(args))

	@base.admin
	@base.room_only
	@base.response
	def disallow(self, bot, room, user, args):
		if len(args) < 1:
			return u"Must specify a permission..."
		else:
			auths = set(room["auths"]) - set(args)
			room["auths"] = list(auths)
			room.save()

			return u"Ok, disallowing the following authorizations: {0}".format(repr(args))

	@base.room_only
	@base.response
	def auths(self, bot, room, user, args):
		return u"I currently have the following authorizations for the {0} room: {1}".format(room.uid, ', '.join(room["auths"]))

module = CoreCommandsModule()