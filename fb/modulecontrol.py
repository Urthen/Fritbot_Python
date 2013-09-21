import sys, traceback, random

from fb.config import cfg
from fb.audit import log
import fb.modules

class ModuleLoader(object):

	def __init__(self):
		self._modules = {}
		self._available_modules = {}

	def refreshAvailableModules(self): 		
		self._available_modules = {}
		errors = False

		#Check to see if we've installed any new modules
		reload(fb.modules)

		for name in fb.modules.__all__:
			if name[0] == '_':
				continue #Not a real module

			fullname = "fb.modules." + name           
				
			try:
				if fullname in sys.modules:
					reload(sys.modules[fullname])
					if 'children' in sys.modules[fullname].__dict__.keys():
						for child in sys.modules[fullname].children:
							reload(child)
				else:
					_module = __import__(fullname, globals(), locals(), ['module'], -1)
			except:
				log.msg("Error loading module: " + fullname + "\n" + traceback.format_exc(), log.ERROR)				
				errors = True
				continue
			
			try:
				module = sys.modules[fullname].module
			except AttributeError:
				pass #not a real module, pass.
			else:
				self._available_modules[name] = module

		log.msg("Available modules: " + str(self._available_modules.keys()))

		return errors

	def renderModule(self, module):
		return {
			'id': module.uid,
			'name': module.name,
			'author': module.author,
			'description': module.description,
			'locked': module.uid in cfg.bot.modules,
			'loaded': module.uid in self._modules,
			'children': [self.renderModule(child.module) for child in module.children],
			'commands': module.commands,
			'listeners': module.listeners,
			'apis': module.apis.keys()
		}

	@property
	def available_modules(self): 
		result = []
		for module in self._available_modules.values():
			result.append(self.renderModule(module))
		return result

	@property
	def installed_modules(self): 
		result = []
		for module in self._modules.values():
			result.append(self.renderModule(module))
		return result

	def installModule(self, name):		
		if name in self._available_modules:
			self.registerModule(self, self._available_modules[name], name)
		else:
			raise KeyError(name + " not found in available modules!")

	def registerModule(self, module, name):
		log.msg("Registering module: " + name)
		try:
			moduleobject = module()
		except:
			log.msg("Error initializing module " + name, log.ERROR)
			raise

		self._modules[name] = moduleobject

		try:
			moduleobject.register()
		except:
			log.msg("Error registering module " + name + "\nSystem may be in a bad state.", log.ERROR)
			raise

	def loadModules(self):
		log.msg("Loading modules...")
		#reload the config, in case it's changed since we started

		try:
			cfg.loadConfig()
		except:
			log.msg("Error loading config:\n" + traceback.format_exc(), log.ERROR)
			return True

		errors = self.refreshAvailableModules()

		# Register active modules.
		for name in cfg.bot.modules:
			if name in self._available_modules:
				self.registerModule(self._available_modules[name], name)
			else:
				log.msg("%s not found in available modules, cannot be activated." % name, log.ERROR)

		return errors

moduleLoader = ModuleLoader()