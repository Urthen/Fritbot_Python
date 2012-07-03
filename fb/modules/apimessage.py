import zope.interface

from fb.api.core import api
from fb.api.util import returnjson, APIResponse
from fb.modules.base import IModule
from fb.api.simple import SimpleFunction
from fb.api.core import api
from fb import security

class APIMessageModule(APIResponse):
	zope.interface.implements(IModule)

	name="API Messaging Service"
	description="Simple messaging service to allow external programs to direct the bot to message users or rooms."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		apimodule = api.registerModule('message')
		apimodule.putChild('room', SimpleFunction(self.room_message))
		apimodule.putChild('user', SimpleFunction(self.user_message))

	@returnjson
	def room_message(self, request):
		if 'key' in request.args:
			data = security.getKeyInfo(request.args['key'][0])
			if data is None:
				return self.error(request, self.UNAUTHORIZED)
		else:
			return self.error(request, self.UNAUTHORIZED)
		if not 'id' in request.args:
			return self.error(request, 400, "Room id not specified.")
		if not 'message' in request.args:
			return self.error(request, 400, "Message not specified.")

		room = api.bot.getRoom(request.args['id'][0]);
		if room is None:
			return self.error(request, 400, "Bot is not in that room.")

		room.send(request.args['message'][0])

		return {'state': 'Message sent.'}

	@returnjson
	def user_message(self, request):
		if not 'id' in request.args:
			return self.error(request, 400, "User id not specified.")
		if not 'message' in request.args:
			return self.error(request, 400, "Message not specified.")

		user = api.bot.getUser(request.args['id'][0]);
		if user is None:
			return self.error(request, 400, "Bot cannot talk to that user.")

		user.send(request.args['message'][0])

		return {'state': 'Message sent.'}

module = APIMessageModule()