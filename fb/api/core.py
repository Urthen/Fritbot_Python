from os import path

from twisted.python import log
from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.server import Site
from twisted.application.internet import TCPServer

from fb.api.simple import SimpleModule
from fb.api import util
from fb.config import cfg

class APIRoot(Resource):

	def __init__(self):
		Resource.__init__(self)
		self.staticRoot = Resource()
		self.putChild('static', self.staticRoot)
		self.staticRoot.putChild('web', File('web/'))
		self.moduleAssist = ModuleAssist()
		self.putChild('moduleassist', self.moduleAssist)

	def launch(self, service):
		log.msg("Starting up the API...")
		TCPServer(cfg.api.port, Site(self)).setServiceParent(service)

	def registerModule(self, name, module, static_dir = None):
		assert name not in ['static', 'web', 'moduleassist'], "Module name %s has been reserved" % name

		log.msg("Registering API path " + name)

		if name in self.children:
			del self.children[name]

		self.putChild(name, module)

		if static_dir:
			self.staticRoot.putChild(name, File(path.join('fb', 'modules', static_dir, '')))
			self.moduleAssist.addModule(name, static_dir)

		return module

	def removeModule(name):
		if name in self.children:
			del self.children[name]
		if name in self.staticRoot.children:
			del self.staticRoot.children[name]
			self.moduleAssist.removeModule(name)

class ModuleAssist(util.APIResponse):
	isLeaf=True

	def __init__(self):
		util.APIResponse.__init__(self)
		self.modules = []

	@util.returnjson
	def render(self, request):
		return {"modules": self.modules}

	def addModule(self, name, dir):
		self.modules.append(name)

	def removeModule(self, name):
		del self.modules[name]

api = APIRoot()