from twisted.python import log
from twisted.web.resource import Resource

from fb.api.quotes import HistoryList
from fb.api.messaging import GroupChat
from fb.api.auth import Retriever

class fbapi(Resource):

	def __init__(self):
		log.msg("Setting up the API...")
		Resource.__init__(self)

		self.putChild("history", HistoryList())
		self.putChild("groupmessage", GroupChat())
		self.putChild("auth", Retriever())
	