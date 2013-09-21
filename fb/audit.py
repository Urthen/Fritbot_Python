import logging, sys

from twisted.python.logfile import DailyLogFile
from twisted.python import log as twistedlogger

from fb.config import cfg

class Auditor(object):

	CRITICAL = 0
	ERROR = 1
	WARNING = 2
	INFO = 3
	DEBUG = 4

	def __init__(self):
		self._started = False

	def start(self, service):
		try:
			logfile = DailyLogFile.fromFullPath(cfg.logging.filename)
		except AssertionError:
			raise AssertionError("Assertion error attempting to open the log file: {0}. Does the directory exist?".format(cfg.logging.filename))

		service.setComponent(twistedlogger.ILogObserver, twistedlogger.FileLogObserver(logfile).emit)
		twistedlogger.startLogging(sys.stdout)

		self._started = True

	def msg(self, text, level=INFO):
		if self._started:
			twistedlogger.msg(text)
		else:
			print text

	def auditCommand(self, room, user, command):
		pass

	def auditResponse(self, room, user, response):
		pass

log = Auditor()