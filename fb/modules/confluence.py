import xmlrpclib

from twisted.python import log

import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response
from fb.config import cfg

class ConfluenceModule:
	zope.interface.implements(IModule)

	name="Confluence"
	description="Functionality for searching Confluence"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("confluence", self.confluence, self, "Confluence Search", "Returns confluence search result, use 'confluence more' to find up to 5 results.")

	@response
	def confluence(self, bot, room, user, args):
		more = False
		results = 1
		if args[0] == "more":
			more = True
			results = 5
			args = args[1:]

		
		try:
			s = xmlrpclib.Server(cfg.confluence.url)
		except:
			return "Confluence URL failure, cannot search Confluence. Contact your bot admin."

		try:
			token = s.confluence1.login(cfg.confluence.username, cfg.confluence.password)
		except:
			return "Login failure, cannot search Confluence. Contact your bot admin."

		search = s.confluence1.search(token, ' '.join(args), results)

		if len(search) > 0:
			if more:
				lines = []
				line = 0
				for l in search:
					line +=1 
					lines.append("{0}: {1} - {2}".format(line, unicode(l['title']), unicode(l['url'])))
				return '\n'.join(lines)
			else:
				return "{0} - {1}".format(unicode(search[0]['title']), unicode(search[0]['url']))
		else:
			return "Sorry {0}, Confluence reports no results for that query.".format(user['nick'])

module = ConfluenceModule()