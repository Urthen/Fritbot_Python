from fb import security

def authorize(bot, room, user, args):
	if room is not None:
		if len(args) > 0:
			security.cancelLogin(args[0])
		return u"%s: For obvious security reasons, don't perform authentication in a public chat setting! I've deleted that token so your unscrupulous colleages don't steal it, please request another." % user['nick']
	if len(args) == 0:
		return u"You've got to specify what login token you want to allow."

	result = security.tokenLogin(args[0], user)

	if result is None:
		return u"That key appears to be valid, but the requestor is no longer listening. You may have closed a web page. Since these are one-use keys, you must request a new key. and attempt to authorize again."
	elif result is False:
		return u"That doesn't seem to be a valid token, sorry!"
	else:
		return u"""Token accepted for application '{0}'. This application has been provided an API key and will now be able to issue commands to Fritbot as if they were you.\n
If this is not what you meant to do, or you wish to later on revoke access to this application, type 'revoke "{0}"'.\n
To see all keys you currently have approved, type 'list keys'.""".format(result)

def authorizations(bot, room, user, args):
	if 'authorizations' in user.info and len(user['authorizations']) > 0:
		out = ['Below are the applications that you have granted access to.']
		for key, data in user['authorizations'].items():
			out.append('<{0}> granted {1}'.format(key, data['date'].strftime("%H:%M %D")))
		return '\n'.join(out)
	else:
		return "You don't have any applications authorized to use Fritbot as you."

def revoke(bot, room, user, args):
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