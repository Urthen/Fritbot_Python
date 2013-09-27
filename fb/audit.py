import logging, sys

from twisted.python.logfile import DailyLogFile
from twisted.python import log as twistedlogger

from fb.config import cfg

class Auditor(object):

	CRITICAL = logging.CRITICAL
	ERROR = logging.ERROR
	WARNING = logging.WARNING
	INFO = logging.INFO
	DEBUG = logging.DEBUG

	def __init__(self):
		try:
			logfile = DailyLogFile.fromFullPath(cfg.logging.filename)
		except AssertionError:
			raise AssertionError("Assertion error attempting to open the log file: {0}. Does the directory exist?".format(cfg.logging.filename))

		twistedlogger.startLogging(logfile, setStdout=False)

	def msg(self, text, level=INFO):
		print text

	def auditCommand(self, room, user, command):
		pass

	def auditResponse(self, room, user, response):
		pass

log = Auditor()
