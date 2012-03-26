from fb.api.util import APIResponse, returnjson

class SimpleModule(APIResponse):

	def __init__(self):
		APIResponse.__init__(self)
		self.apichildren = {}

	def putChild(self, name, child):
		self.apichildren[name] = child
		APIResponse.putChild(self, name, child)

	def putSimpleChild(self, name, f):
		self.putChild(name, SimpleChild(f))

	@returnjson
	def render(self, request):
		return self.error(request, self.NOT_FOUND, "Valid API Module, but you must specify an actual function! Valid functions are: {0}".format(', '.join(self.apichildren.keys())))

class SimpleChild(APIResponse):
	def __init__(self, f):
		self.render = f
		APIResponse.__init__(self)
		