from twisted.python import log
 	
def response(f):
	def responder(self, bot, room, user, args):
		out = f(self, bot, room, user, args)

		if out is None:
			return False

		if type(out) == type(u'') or type(out) == type(''):
			if room is not None:
				room.send(out)
			else:
				user.send(out)
			return True

		log.msg("Invalid type returned by function wrapped by @response: {0} - {1}".format(out, type(out)))
		return False

	return responder

class FritbotModule(object):
	
	name="Basic Module"
	description="Basic Module Description"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"
	requirements = []

	def register(self, bot):
		raise NotImplementedError("register must be overridden by a subclass!")