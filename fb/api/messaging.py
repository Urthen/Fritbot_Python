from twisted.python import log


from twisted.web.error import NoResource

from fb import db
from fb.api.util import returnjson, APIResponse

class GroupChat(APIResponse):
	def getChild(self, name, request):
		return GroupChatRoom(name)

class GroupChatRoom(APIResponse):
	def __init__(self, resource):
		self.room = resource

	@returnjson
	def render_GET(self, request):
		query = {"_id": self._id}
		print query
		quote = db.db.history.find_one(query)
		if quote:
			return HistoryObj(quote)
		else:
			request.setResponseCode(404)
			return {'errors': True, 'error': 'History item not found.'}