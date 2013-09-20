import sys, traceback

from fb.config import cfg
from fb.audit import log

class ModuleLoader(object):

	def __init__(self):
		self._modules = {}

	def registerModule(self, module, name):
		log.msg("Registering module: " + name)
		try:
			moduleobject = module.module
		except:
			log.msg("'module' object not created in module: " + name)
			raise
		self._modules[name] = moduleobject
		moduleobject.register()

	def loadModules(self):
		log.msg("Loading modules...")
		#reload the config, in case it's changed since we started

		try:
			cfg.loadConfig()
		except:
			log.msg("Error loading config:\n" + traceback.format_exc(), log.ERROR)
			return True

		errors = False

		# Import and register configured modules.
		for name in cfg.bot.modules:
			log.msg("Loading module {0}...".format(name))
			fullname = "fb.modules." + name           
				
			try:
				if fullname in sys.modules:
					reload(sys.modules[fullname])
					if 'children' in sys.modules[fullname].__dict__.keys():
						for child in sys.modules[fullname].children:
							reload(child)
				else:
					__import__(fullname, globals(), locals(), [], -1)

			except:
				log.msg("Error loading module: " + fullname + "\n" + traceback.format_exc(), log.ERROR)
				errors = True
				
			else:	
				if fullname in sys.modules:
					module = sys.modules[fullname]
					self.registerModule(module, name)

		return errors

moduleLoader = ModuleLoader()