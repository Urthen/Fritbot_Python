import fb.intent as intent
from fb.api import security
from fb.modules.base import Module, response

class SecurityModule(Module):

	uid="chat_core.security"
	name="Security"
	description="Security and API access related commands"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	commands = {
		"authorize": {
			"keywords": "authorize",
			"function": "authorize",
			"name": "Authorize",
			"description": "Authorize given API key"
		},
		"revoke": {
			"keywords": "revoke",
			"function": "revoke",
			"name": "Revoke",
			"description": "Revokes given API key authorization"
		},
		"listkeys": {
			"keywords": "list keys",
			"function": "authorizations",
			"name": "Key List",
			"description": "List all authorized API Keys and what applications they go to"
		}
	}

	@response
	def authorize(self, bot, room, user, args):
		if room is not None:
			if len(args) > 0:
				security.cancelLogin(args[0])
			return "%s: For obvious security reasons, don't perform authentication in a public chat setting! I've deleted that token so your unscrupulous colleages don't steal it, please request another." % user['nick']
		if len(args) == 0:
			return "You've got to specify what login token you want to allow."

		print args[0], user

		result = security.tokenLogin(args[0], user)

		if result is None:
			return "That key appears to be valid, but the requestor is no longer listening. You may have closed a web page. Since these are one-use keys, you must request a new key. and attempt to authorize again."
		elif result is False:
			return "That doesn't seem to be a valid token!"
		else:
			return """Token accepted for application '{0}'. This application has been provided an API key and will now be able to issue commands to Fritbot as if they were you.\n
If this is not what you meant to do, or you wish to later on revoke access to this application, type 'revoke "{0}"'.\n
To see all keys you currently have approved, type 'list keys'.""".format(result)

	@response
	def authorizations(self, bot, room, user, args):
		if 'authorizations' in user.info and len(user['authorizations']) > 0:
			out = ['Below are the applications that you have granted access to.']
			for data in user['authorizations']:
				out.append('<{0}> granted {1}'.format(data['app'], data['date'].strftime("%H:%M %D")))
			return '\n'.join(out)
		else:
			return "You don't have any applications authorized to use Fritbot as you."

	@response
	def revoke(self, bot, room, user, args):
		if 'authorizations' in user.info and len(user['authorizations']) > 0:
			if len(args) == 0:
				return "You must specify an application (or applications) to revoke the key from, or use 'revoke all' to revoke all approved keys."

			out = ["Revoking keys..."]
			for app in args:
				if security.revokeKey(user, app):
					out.append("Revoked key for '%s'." % app)
				else:
					out.append("App '%s' doesn't have a key from you. (did you forget quotation marks?)" % app)
			return '\n'.join(out)
		else:
			return "You don't have any applications authorized to use Fritbot as you, so there is nothing to revoke."

module = SecurityModule