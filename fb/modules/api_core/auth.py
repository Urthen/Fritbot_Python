import json

from twisted.web.server import NOT_DONE_YET

from fb.api.util import returnjson, APIResponse
from fb.modules.base import Module
from fb.api import security
from fb.api.core import api
from fb.config import cfg

class KeyAPI(APIResponse):
	isLeaf = True

	@returnjson
	def render_GET(self, request):
		if len(request.postpath) == 1:
			data = security.getKeyInfo(request.postpath[0])
			if data is not None:
				return data
		return self.error(request, self.NOT_FOUND, "Key not specified, not recognized, or expired.")

class APIAuthModule(Module):

	uid="api_core.auth"
	name="API Authentication Module"
	description="Authentication module for requesting keys to be verified by users."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	apis={
		'key': KeyAPI()
	}

module = APIAuthModule