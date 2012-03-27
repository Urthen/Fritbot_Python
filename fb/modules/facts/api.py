import zope.interface

import fb.intent as intent
from fb.modules.base import IModule
from fb.db import db, OID
from fb.api.core import api
from fb.api.util import APIResponse, APIError, returnjson
from fb.api.simple import SimpleFunction, SimpleData

class FactsAPIModule:
	zope.interface.implements(IModule)


	name="Facts API Module"
	description="API Segment of the Facts module."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self, parent):
		apimodule = api.registerModule('facts', FactsList())

class FactObj(dict):
	def __init__(self, row):
		self['id'] = str(row['_id'])
		self['created'] = str(row['created'])
		self['factoids'] = row['factoids']
		self['count'] = row['count']
		self['triggers'] = row['triggers']
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
	pass

module = FactsAPIModule()
