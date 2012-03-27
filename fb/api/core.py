from twisted.python import log
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.application.internet import TCPServer

from fb.api.quotes import HistoryList
from fb.api.messaging import GroupChat
from fb.api.auth import Retriever
from fb.api.simple import SimpleModule
from fb.api import util

import config

class APIRoot(Resource):

	def __init__(self):
		log.msg("Setting up the API...")
		Resource.__init__(self)

		self.putChild("history", HistoryList())
		self.putChild("groupmessage", GroupChat())
		self.putChild("auth", Retriever())

	def addModule(self, name, module):
		self.putChild(name, module)

class APIWrapper(object):

	def __init__(self):
		self.root = None
		self.preregistered = {}

	def launch(self, application):
		if 'security' not in config.APPLICATION['modules']:
			log.msg("Warning: You have the API enabled, but not the 'security' module!")

		# Initialize the API
		self.root = APIRoot()

		TCPServer(config.API['port'], Site(self.root)).setServiceParent(application)
		for module in self.preregistered:
			self.root.addModule(module, self.preregistered[module])

		self.preregistered = []

	def registerModule(self, name, module = None):
		if module is None:
			module = SimpleModule()
		if self.root is None:
			self.preregistered[name] = module
		else:
			self.root.addModule(name, module)

		return module
	
api = APIWrapper()