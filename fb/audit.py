import logging, sys

from twisted.python.logfile import DailyLogFile
from twisted.python import log as twistedlogger

import config

class Auditor(object):

	CRITICAL = 0
	ERROR = 1
	WARNING = 2
	INFO = 3
	DEBUG = 4

	def start(self, application):
		try:
			logfile = DailyLogFile(config.LOG["filename"], config.LOG["directory"])
		except AssertionError:
			raise AssertionError("Assertion error attempting to open the log file. Does the directory {0} exist?".format(config.LOG["directory"]))

		application.setComponent(twistedlogger.ILogObserver, twistedlogger.FileLogObserver(logfile).emit)
		twistedlogger.startLogging(sys.stdout)

	def msg(self, text, level=INFO):
		twistedlogger.msg(text)

	def auditCommand(self, room, user, command):
		pass

	def auditResponse(self, room, user, response):
		pass

log = Auditor()