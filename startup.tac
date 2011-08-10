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
from wokkel.client import XMPPClient

from fb.fritbot import FritBot
from fb.interface.jabber import JabberInterface
import config

# Set up twistd application
application = service.Application(config.APPLICATION["name"])

try:
	logfile = DailyLogFile(config.LOG["filename"], config.LOG["directory"])
except AssertionError:
	raise AssertionError("Assertion error attempting to open the log file. Does the directory {0} exist?".format(config.LOG["directory"]))

application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
log.startLogging(sys.stdout)

# Set up Fritbot instance
fritbot = FritBot()

# Connect to XMPP
xmppclient = XMPPClient(jid.internJID(config.JABBER["jid"]), config.JABBER["password"], config.JABBER["server"])
xmppclient.logTraffic = config.LOG["traffic"]

jinterface = JabberInterface(fritbot)
jinterface.setHandlerParent(xmppclient)
xmppclient.setServiceParent(application)