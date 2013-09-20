from twisted.python import log

import zope.interface

import fb.intent as intent
from fb.modules.base import IModule, response
from fb.config import cfg

#for jira ticket info
import SOAPpy, getpass, datetime, array, base64, random
from SOAPpy import Types

class JIRAModule:
	zope.interface.implements(IModule)

	name="JIRA"
	description="Functionality for searching Jira"
	author="Kyle Varga (kyle.varga@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("jira", self.jira, self, "JIRA Search", "Returns jira search result")

	@response
	def jira(self, bot, room, user, args):
		if 'jira' not in cfg._cfg:
			return 'JIRA disabled, must be added to config'
			
		try:
			eol = '\r\n '
			ticketNum = args[0]
			if ticketNum.isdigit():
				ticketNum = cfg.jira.default_project + ticketNum
			print ticketNum
			soap = SOAPpy.WSDL.Proxy(cfg.jira.url)
			auth = soap.login(cfg.jira.username, cfg.jira.password)
			myissue = soap.getIssue(auth, ticketNum)
			link = cfg.jira.link_prefix + ticketNum;
			
			returnString = link+ eol
			returnString += myissue.summary + eol
			returnString += 'Reporter: ' + myissue.reporter + eol if isinstance(myissue.reporter,str) else 'None' + eol
			
			
			assignee = myissue.assignee
			if not isinstance(assignee,str):
				assignee = 'Unassigned'
			returnString += 'Assignee: ' + assignee
			#returnString += 'Status: ' + myissue.status + eol        
			
			return returnString
		except:
			return 'Oh no! Jira errors bad!'

module = JIRAModule()
