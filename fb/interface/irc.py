'''Fritbot IRC interface
Connects to and handles all communication with an IRC server.'''

import sys, datetime
from twisted.internet import defer, reactor
from twisted.python import log
from twisted.words.protocols import irc

import fb.fritbot as FritBot
from interface import Interface, User, Room
from fb.db import db
import config, fb.intent as intent