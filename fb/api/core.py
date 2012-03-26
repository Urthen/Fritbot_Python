from twisted.python import log
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.application.internet import TCPServer

from fb.api.quotes import HistoryList
from fb.api.messaging import GroupChat
from fb.api.auth import Retriever

import config

class APIRoot(Resource):

	def __init__(self):
		log.msg("Setting up the API...")
		Resource.__init__(self)

		self.putChild("history", HistoryList())
		self.putChild("groupmessage", GroupChat())
		self.putChild("auth", Retriever())

	def addModule(self, module):
		self.putChild(module)

class APIWrapper(object):

	def __init__(self):
		self.root = None
		self.preregistered = []

	def launch(self, application):
		if 'security' not in config.APPLICATION['modules']:
			log("Warning: You have the API enabled, but not the 'security' module!")

		# Initialize the API
		self.root = APIRoot()

		TCPServer(config.API['port'], Site(self.root)).setServiceParent(application)
		for module in self.preregistered:
			self.root.addModule(module)

		self.preregistered = []

	def registerModule(self, module):
		if self.root is None:
			self.preregistered.append(module)
		else:
			self.root.addModule(module)
	
api = APIWrapper()