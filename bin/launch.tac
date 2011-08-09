'''
launch.tac: Twistd application file used to launch an actual fritbot instance.
To launch in console mode, run "twistd -ny launch.tac"
'''

from twisted.application import service
from twisted.words.protocols.jabber import jid
from twisted.python.logfile import DailyLogFile
from wokkel.client import XMPPClient

from fritbot import FritBot
from jabber import JabberInterface
import config

# Set up twistd application
application = service.Application(config.APPLICATION["name"])
logfile = DailyLogFile(config.LOG["filename"], config.LOG["directory"])

# Set up Fritbot instance
fritbot = FritBot()

# Connect to XMPP
xmppclient = XMPPClient(jid.internJID(config.JABBER["jid"]), config.JABBER["password"])
xmppclient.logTraffic = config.LOG["traffic"]

jinterface = JabberInterface(fritbot)
jinterface.setHandlerParent(xmppclient)
xmppclient.setServiceParent(application)