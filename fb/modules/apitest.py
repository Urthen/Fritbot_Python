import zope.interface

from fb.api.core import api
from fb.api.util import returnjson
from fb.modules.base import IModule

class APITestModule:
	zope.interface.implements(IModule)

	name="API Test"
	description="Simple test demonstration of module API functionality"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		apimodule = api.registerModule('apitest')
		apimodule.putSimpleChild('hello', self.hello)

	@returnjson
	def hello(self, request):
		return {'greeting': 'Hello, the API works!'}


module = APITestModule()