import fb.intent as intent
from fb.api import security
from fb.modules.base import Module, response, user_only

class SecurityModule(Module):

	uid="chat_core.security"
	name="Security"
	description="Security and API access related commands"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	commands = {
		"getkey": {
			"keywords": "get key",
			"function": "getkey",
			"name": "Get API Key",
			"description": "Gives you an API key for use in fritbot-enabled applications. Usage: get key 'app name'"
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

	@user_only
	@response
	def getkey(self, bot, room, user, args):
		result = security.getKey(args[0], user)
		
		return """Token granted for application '{0}': '{1}'.\nProviding this key to an application will it to issue commands to Fritbot as if they were you.
If this is not what you meant to do, or you wish to later on revoke access to this application, type 'revoke "{0}"'.\n
To see all keys you currently have approved, type 'list keys'.""".format(args[0], result)

	@response
	def authorizations(self, bot, room, user, args):
		if 'authorizations' in user.info and len(user['authorizations']) > 0:
			out = ['Below are the applications that you have granted access to.']
			for data in user['authorizations']:
				out.append('{2} <{0}> granted {1}'.format(data['app'], data['date'].strftime("%H:%M %D"), data['key']))

			out.append("\nTo revoke a key, type revoke 'applicationname'")
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