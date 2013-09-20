'''
Twisted service definition for running FritBot
'''

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import service

class Options(usage.Options):
	synopsis = "[options] configfiles..."
	optFlags = [
		['showconfig', None, "Dump the parsed configuration after loading"]
	]
	
	def parseArgs(self, *args):
		'''Remaining args should be a list of configuration files.'''
		self['configs'] = args

class FritbotFactory(object):
	implements(IServiceMaker, IPlugin)
	tapname = "fritbot"
	description = "The angriest bot."
	options = Options

	def makeService(self, options):
		import sys
		from fb.config import cfg

		cfg.loadConfig(options['configs'])

		if options['showconfig']:
			cfg._cfg.dump(sys.stdout)

		from fb.audit import log

		# Friendly warning - I ran into this once, hopefully this will help others in the future.
		try:
			from OpenSSL import SSL
		except:
			log.msg("Warning, we can't import SSL. You may have trouble connecting to some servers. If so, try installing pyOpenSSL.")

		if cfg.connect.method not in cfg.connect:
			log.msg("Connector %s specified but not found in settings." % config.connect.method)
			sys.exit(1)

		try:
			connector = __import__('fb.connectors.' + cfg.connect.method, globals(), locals(), ['createService'], -1)
		except ImportError:
			log.msg("Coudln't import connector: %s" % cfg.connect.method)
			raise

		log.msg("Successfully loaded connector %s" % cfg.connect.method)

		return connector.createService()

fritbotFactory = FritbotFactory();
