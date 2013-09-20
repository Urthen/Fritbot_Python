from twisted.python import log
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.application.internet import TCPServer

from fb.api.simple import SimpleModule
from fb.api import util
from fb.config import cfg

class APIRegistrationError(Exception):
	pass

class APIRoot(Resource):

	def __init__(self):
		log.msg("Setting up the API...")
		Resource.__init__(self)

		self.registeredModules = []

	def addModule(self, name, module):
		self.putChild(name, module)

class APIWrapper(object):

	def __init__(self):
		self.root = None
		self.preregistered = {}

	def launch(self, service):
		# Initialize the API
		self.root = APIRoot()

		TCPServer(cfg.api.port, Site(self.root)).setServiceParent(service)
		for module in self.preregistered:
			self.root.addModule(module, self.preregistered[module])

		self.preregistered = []

	def registerModule(self, name, module = None):
		if module is None:
			module = SimpleModule()
		if self.root is None:
			if name in self.preregistered:
				raise APIRegistrationError("A module with the name {0} has already been registered.".format(name))

			self.preregistered[name] = module
		else:
			self.root.addModule(name, module)

		return module
	
api = APIWrapper()