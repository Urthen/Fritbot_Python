from twisted.python import log
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.application.internet import TCPServer

from fb.api.quotes import HistoryList
from fb.api.messaging import GroupChat
from fb.api.auth import Retriever
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

		self.addModule("history", HistoryList())
		self.addModule("groupmessage", GroupChat())
		self.addModule("auth", Retriever())

	def addModule(self, name, module):
		if name in self.registeredModules:
			raise APIRegistrationError("A module with the name {0} has already been registered.".format(name))

		self.putChild(name, module)

class APIWrapper(object):

	def __init__(self):
		self.root = None
		self.bot = None
		self.preregistered = {}

	def launch(self, bot, application):
		if 'security' not in cfg.application.modules:
			log.msg("Warning: You have the API enabled, but not the 'security' module. You will be unable to accept any keys.")

		# Initialize the API
		self.root = APIRoot()
		self.bot = bot

		TCPServer(cfg.api.port, Site(self.root)).setServiceParent(application)
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