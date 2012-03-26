'''
launch.tac: Twistd application file used to launch an actual fritbot instance.
To launch in console mode, run "twistd -ny launch.tac"
'''

import sys

from twisted.words.protocols.jabber import jid
from twisted.application import service

from wokkel.client import XMPPClient

from fb.audit import log
from fb.interface.jabber import JabberInterface
import config

try:
	from OpenSSL import SSL
except:
	log.msg("Warning, we can't import SSL. You may have trouble connecting to some servers. If so, try installing pyOpenSSL.")

# Set up twistd application
application = service.Application(config.APPLICATION["name"])

log.start(application)

# Set up Fritbot chat instance



if hasattr(config, 'API'):
	from fb.api.core import api
	api.launch(application)