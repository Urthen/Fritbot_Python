import zope.interface

import fb.intent as intent
from fb.modules.base import IModule
from fb.db import db
from fb.api.core import api
from fb.api.util import returnjson

class FactsAPIModule:
	zope.interface.implements(IModule)


	name="Facts API Module"
	description="API Segment of the Facts module."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self, parent):
		apimodule = api.registerModule('facts')
		apimodule.putSimpleChild('list', self.apilist)

	@returnjson
	def apilist(self, request):
		factlist = []
		for fact in db.facts.find({}, {'_id': 0}):
			fact['created'] = str(fact['created'])
			for factoid in fact['factoids']:
				factoid['created'] = str(factoid['created'])

			factlist.append(fact)

		return {'facts': factlist}
				

module = FactsAPIModule()
