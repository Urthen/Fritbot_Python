'''
launch.tac: Twistd application file used to launch an actual fritbot instance.
To launch in console mode, run "twistd -ny launch.tac"
'''

import sys

from twisted.application import service
from twisted.words.protocols.jabber import jid
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile
from twisted.python import log

import config

# Set up twistd application
application = service.Application(config.APPLICATION["name"])

try:
	logfile = DailyLogFile(config.LOG["filename"], config.LOG["directory"])
except AssertionError:
	raise AssertionError("Assertion error attempting to open the log file. Does the directory {0} exist?".format(config.LOG["directory"]))

application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
log.startLogging(sys.stdout)

try:
	from OpenSSL import SSL
except:
	log.msg("Warning, we can't import SSL. You may have trouble connecting to some servers. If so, try installing pyOpenSSL.")

# Set up Fritbot chat instance

if config.JABBER:
	from wokkel.client import XMPPClient
	from fb.interface.jabber import JabberInterface

	# Connect to XMPP
	bot_jid = "{0}@{1}/{2}".format(config.JABBER["jid"], config.JABBER["server"], config.JABBER["resource"])
	xmppclient = XMPPClient(jid.internJID(bot_jid), config.JABBER["password"], config.JABBER["server"])
	xmppclient.logTraffic = config.LOG["traffic"]

	# Hook chat instance into main app
	jinterface = JabberInterface()
	jinterface.setHandlerParent(xmppclient)
	xmppclient.setServiceParent(application)

if config.API:
	from twisted.application.internet import TCPServer
	from twisted.web.server import Site
	from fb.api.core import fbapi

	# Initialize the API
	api = fbapi()

	TCPServer(config.API['port'], Site(api)).setServiceParent(application)