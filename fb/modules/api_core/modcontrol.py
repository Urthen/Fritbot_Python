import json

import zope.interface
from twisted.web.server import NOT_DONE_YET

from fb.api.util import returnjson, APIResponse
from fb.modules.base import IModule
from fb.api import security
from fb.api.core import api
from fb.config import cfg
from fb import intent

class ModuleControlAPIModule(APIResponse):
	zope.interface.implements(IModule)

	name="Module Control API"
	description="Module to manage the loading/disabling of other modules via api."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self, parent):
		apimodule = api.registerModule('modcontrol', ModuleController)

class ModuleController(APIResponse):

	def getChild(self, name, request):
		
		if name is "":
			return SimpleFunction(self.module_list)
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
		pass

module = ModuleControlAPIModule()