import zope.interface

from fb.modules.base import IModule
from fb.modules.api_core import auth, modcontrol

class APICoreModule:
	zope.interface.implements(IModule)

	name="API Core"
	description="Core API Modules"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		auth.module.register(self)
		modcontrol.module.register(self)
				
children = [auth, modcontrol]
module = APICoreModule()