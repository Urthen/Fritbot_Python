from twisted.python import log
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.application.internet import TCPServer

from fb.api.simple import SimpleModule
from fb.api import util
from fb.config import cfg

class APIRoot(Resource):

	def __init__(self):
		
		Resource.__init__(self)

class APIRoot(Resource):

	def launch(self, service):
		log.msg("Starting up the API...")
		TCPServer(cfg.api.port, Site(self)).setServiceParent(service)

	def registerModule(self, name, module = None):
		if module is None:
			module = SimpleModule()

		if name in self.children:
			del self.children[name]

		self.putChild(name, module)

		return module
	
api = APIRoot()