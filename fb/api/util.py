import json

from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET

from fb import db
from fb.config import cfg

def parseSortOptions(options):
	out = []
	for option in options:
		if option[-4:] == "_asc":
			out.append((option[:4], db.ASCENDING))
		elif option[-5:] == "_desc":
			out.append((option[:5], db.DESCENDING))
		else:
			out.append((option, db.ASCENDING))
		
	return out

def returnjson(f):
	def jsonResponse(self, request):
		request.setHeader('Access-Control-Allow-Origin', '*')
		request.setHeader("Content-Type", "application/json")
		try:
			out = f(self, request)
		except:
			if cfg.api.debug == "True":
				raise
			else:
				out = self.error(request)
		
		if out == NOT_DONE_YET:
			return out
		else:
			return json.dumps(out)

	return jsonResponse


class APIResponse(Resource):

	OK = 200 # Status code for generic OK - realistically, this is always passed by Twisted itself and shouldn't need to be specified.
	CREATED = 201 # Status code for created new object in the DB
	ACCEPTED = 202 # Usually for "We've sent the message, no idea if it's recieved."
	BAD_REQUEST = 400 # Status code for syntax errors, etc
	UNAUTHORIZED = 401 # API Key needs to be provided for this request.
	FORBIDDEN = 403 # API Key does not have the appropriate permissions for this request.
	NOT_FOUND = 404 # Requested resource wasn't found.
	METHOD_NOT_ALLOWED = 405 # Request method (GET, POST, etc) not allowed for this URI
	GONE = 410 # Request was there, but is gone now and won't be coming back.
	IM_A_TEAPOT = 418 # Requestor was expecting a Coffee Pot, but this is a Tea Pot.
	THRESHOLD = 429 # API Key has had too many requests for a period of time.
	SERVER_ERROR = 500 # Generic server error.

	_default_messages  = {
		200: "OK",
		201: "Created.",
		202: "Accepted.",
		400: "Bad request, fix your URI!",
		401: "You must provide an API Key for this request.",
		403: "Provided API key does not have sufficient permissions for this request.",
		404: "Requested resource not found.",
		405: "Request method is not allowed at this URI.",
		410: "Gone! I know what you're talking about, but it isn't here anymore.",
		418: "I'm a little teapot, short and stout.",
		429: "API Key threshold exceeded, try again in a few seconds.",
		500: "Server error, request cannot be completed at this time."
	}
	
	def error(self, request, response=None, message=None):
		if response is None:
			response = self.SERVER_ERROR #probably accurate, because i've forgotten to put an error code anyway.

		request.setResponseCode(response)
		if message is None:
			if response in self._default_messages:
				message = self._default_messages[response]

		if message is not None:
			return {'errors': True, 'error': message}
		else:
			return {'errors': True}

	@returnjson
	def render_GET(self, request):
		return self.error(request, 405)

	@returnjson
	def render_POST(self, request):
		return self.error(request, 405)

	@returnjson
	def render_DELETE(self, request):
		return self.error(request, 405)

	@returnjson
	def render_PUT(self, request):
		return self.error(request, 405)

	@returnjson
	def render_OPTIONS(self, request):
		return self.error(request, 405)

class APIError(APIResponse):
	def __init__(self, code=None, message=None):
		self.code = code
		self.message = message

	@returnjson
	def render(self, request):
		return self.error(request, self.code, self.message)