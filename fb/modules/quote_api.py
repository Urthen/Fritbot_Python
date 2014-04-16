import json

from twisted.python import log

from twisted.web.resource import Resource, NoResource
from twisted.web.static import Data

from fb import db
from fb.api.util import returnjson, parseSortOptions, APIResponse, APIError

import fb.config

class HistoryObj(dict):
	def __init__(self, row):
		self['id'] = str(row['_id'])
		self['user'] = {'nick': row['user']['nick']}
		if 'id' in row['user']:
			self['user']['id'] = str(row['user']['id'])
		self['body'] = row['body']
		if 'date' in row:
			self['date'] = row['date'].isoformat()
		if 'room' in row:
			room = db.db.getRoomInfo(row['room'])
			if room:
				self['room'] = {
					'id': str(row['room']),
					'name': room['name']
					}

		if 'remembered' in row:
			self['remembered'] = {
				'nick': row['remembered']['nick'],
				'date': row['remembered']['time'].isoformat()
			}
			if 'user' in row['remembered']:
				self['remembered']['user'] = str(row['remembered']['user'])

class HistoryList(APIResponse):
	def getChild(self, name, request):
		try: 
			id = db.OID(name)
		except:
			return APIError(self.BAD_REQUEST, "That isn't a valid ID.")

		query = {"_id": id}
		quote = db.db.history.find_one(query)
		if quote:
			return HistoryItem(quote)
		else:
			return APIError(self.NOT_FOUND)


	@returnjson
	def render_GET(self, request):
		query = {}
		quotes = db.db.history.find(query)

		sort = [('date', db.DESCENDING)]
		quotes.sort(sort)

		limit = cfg.api.default_limit
		if 'limit' in request.args:
			try:
				limit = int(request.args['limit'][0])
			except:
				return self.error(request, self.BAD_REQUEST, "Limit couldn't be parsed into an integer.")
			if limit > cfg.api.max_limit:
				limit = cfg.api.max_limit

		
		quotes.limit(limit)

		outlist = []
		for quote in quotes:
			outlist.append(HistoryObj(quote))

		return {'quotes':outlist}

class HistoryItem(APIResponse):
	def __init__(self, row):
		self.row = row
	
	@returnjson
	def render_GET(self, request):
		return HistoryObj(self.row)