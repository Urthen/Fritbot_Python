
from fb.api.core import api
from fb.api.util import returnjson, APIResponse
from fb.modules.base import Module
from fb.api.simple import SimpleFunction

class APITestResponse(APIResponse):

	def __init__(self):
		APIResponse.__init__(self)
		self.putChild("hello", SimpleFunction(self.hello))
	
	@returnjson
	def hello(self, request):
		return {'greeting': 'Hello, the API works!'}

class APITestModule(Module):
	
	uid="apitest"
	name="API Test"
	description="Simple test demonstration of module API functionality"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	apis = {
		"apitest": APITestResponse()
	}

module = APITestModule
