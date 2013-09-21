import fb.intent as intent
from fb.modules.base import Module
from fb.db import db, OID
from fb.api.core import api
from fb.api.util import APIResponse, APIError, returnjson
from fb.api.simple import SimpleFunction, SimpleData
from fb.api import security

from fb.modules.facts import commands

class FactObj(dict):
	def __init__(self, row):
		self.row = row
		self['id'] = str(row['_id'])
		self['created'] = str(row['created'])
		self['factoids'] = row['factoids']
		self['count'] = row['count']
		self['triggers'] = row['triggers']
		if 'removed' in row:
			self['removed'] = row['removed']
		else:
			self['removed'] = False
		for factoid in self['factoids']:
			factoid['created'] = str(factoid['created'])

class FactsList(APIResponse):

	def getChild(self, name, request):
		
		if name is "":
			return SimpleFunction(self.apilist)
		else:
			try:
				factid = OID(name)
			except:
				return APIError(self.BAD_REQUEST, "That isn't a valid ID.")
			
			fact = db.facts.find_one({'_id': factid})
			if fact is None:
				return APIError(self.NOT_FOUND, "Fact doesn't exist.")
				 
			return FactItem(FactObj(fact))

	@returnjson
	def apilist(self, request):
		factlist = []
		for row in db.facts.find({}).sort('count', -1):
			fact = FactObj(row)
			factlist.append(fact)

		return {'facts': factlist}			

class FactItem(SimpleData):
	
	@returnjson
	def render_DELETE(self, request):
		if 'key' in request.args:
			data = security.getKeyInfo(request.args['key'][0])
			if data is not None:
				self.data.row['removed'] = data['userid']
				db.facts.update({'_id': OID(self.data['id'])}, self.data.row)
				commands.module.refresh()
				return FactObj(self.data.row)

		return self.error(request, self.UNAUTHORIZED)

class FactsAPIModule(Module):

	uid="facts.api"
	name="Facts API Module"
	description="API Segment of the Facts module."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	apis={
		"facts": FactsList()
	}

module = FactsAPIModule
