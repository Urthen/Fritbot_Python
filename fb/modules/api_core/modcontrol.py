import json

from twisted.web.server import NOT_DONE_YET

from fb.api.util import returnjson, APIResponse
from fb.modules.base import Module
from fb.api import security
from fb.api.simple import SimpleFunction
from fb.api.core import api
from fb.config import cfg
from fb.modulecontrol import moduleLoader

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
	def module_list(self, request):
		
		modules = []

		return {"modules": moduleLoader.available_modules}


class ModuleControlAPIModule(Module):

	uid="api_core.modcontrol"
	name="Module Control API"
	description="Module to manage the loading/disabling of other modules via api."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	apis = {
		'modcontrol': ModuleController()
	}

module = ModuleControlAPIModule