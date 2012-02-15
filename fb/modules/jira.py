from twisted.python import log

import config
import fb.intent as intent
from fb.modules.base import FritbotModule, response

#for jira ticket info
import SOAPpy, getpass, datetime, array, base64, random
from SOAPpy import Types

# Add to config.py
#JIRA = {
#    "enabled": True,
#    "url": "http://bits.bazaarvoice.com:8080/jira/rpc/soap/jirasoapservice-v2?wsdl",
#    "username": "username",
#    "password": "password",
#    "link_prefix": "https://bits.bazaarvoice.com/jira/browse/",
#    "default_project": "BVC-" # Also include the -, ie. "PRJ-"
#}

class JIRAModule(FritbotModule):

	name="Confluence"
	description="Functionality for searching Jira"
	author="Kyle Varga (kyle.varga@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("jira", self.jira, self, "JIRA Search", "Returns jira search result")

	@response
	def jira(self, bot, room, user, args):
		print config.JIRA
		if not config.JIRA["enabled"]:
			return 'JIRA Disabled'
			
		try:
			eol = '\r\n '
			ticketNum = args[0]
			if ticketNum.isdigit():
				ticketNum = config.JIRA["default_project"] + ticketNum
			print ticketNum
			soap = SOAPpy.WSDL.Proxy(config.JIRA["url"])
			jirauser=config.JIRA["username"]
			passwd=config.JIRA["password"]
			auth = soap.login(jirauser, passwd)
			myissue = soap.getIssue(auth, ticketNum)
			link = config.JIRA["link_prefix"] + ticketNum;
			
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
			return 'oh no! jira down'
module = JIRAModule()