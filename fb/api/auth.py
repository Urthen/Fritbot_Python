import json

from twisted.web.server import NOT_DONE_YET

from fb.api.util import returnjson, APIResponse
from fb import security
import config


class Retriever(APIResponse):

	def __init__(self):
		APIResponse.__init__(self)
		self.putChild('request', KeyRequest())
		self.putChild('response', KeyListener())
		self.putChild('info', KeyInfo())

	@returnjson
	def render(self, request):
		return self.error(request, self.NOT_FOUND, "Must specify a login option, see the API documentation.")

class KeyRequest(APIResponse):
	@returnjson
	def render_GET(self, request):
		if 'application' in request.args:
			if request.args['application'] == 'all':
				return self.error(request, self.IM_A_TEAPOT, "'all' is not a valid application name, but hey, nice try.")
			token = security.getLoginToken(request.args['application'][0])
			return {'token': token, 'timeout': config.API['login_timeout']}
		else:
			return self.error(request, self.BAD_REQUEST, "You must specify an application name for your request.")

class KeyListener(APIResponse):
	isLeaf=True

	def responded(self, user=None, key=None):
		if user is None or key is None:
			self.request.setResponseCode(self.GONE)
			self.request.write(json.dumps({'errors': True, 'error': "Token not accepted by any user."}))
		else:
			self.request.write(json.dumps({'key': key, 'user': user.uid, 'nick': user['nick']}))

		self.request.finish()

	@returnjson
	def render_GET(self, request):
		if len(request.postpath) == 1:
			if security.listenForLogin(request.postpath[0], self.responded):
				self.request = request
				return NOT_DONE_YET
		return self.error(request, self.NOT_FOUND, "Token not specified, not recognized, or expired.")

class KeyInfo(APIResponse):
	isLeaf=True

	@returnjson
	def render_GET(self, request):
		print request.postpath
		if len(request.postpath) == 1:
			data = security.getKeyInfo(request.postpath[0])
			if data is not None:
				return data
		return self.error(request, self.NOT_FOUND, "Key not specified, not recognized, or expired.")