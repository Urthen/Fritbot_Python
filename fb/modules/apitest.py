import zope.interface

from fb.api.core import api
from fb.api.util import returnjson
from fb.modules.base import IModule
from fb.api.simple import SimpleFunction

class APITestModule:
	zope.interface.implements(IModule)

	name="API Test"
	description="Simple test demonstration of module API functionality"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		apimodule = api.registerModule('apitest')
		apimodule.putChild('hello', SimpleFunction(self.hello))

	@returnjson
	def hello(self, request):
		return {'greeting': 'Hello, the API works!'}

module = APITestModule
