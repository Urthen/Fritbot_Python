from fb.modules.base import Module
from fb.modules.api_core import auth, modcontrol

class APICoreModule(Module):

	uid='api_core'
	name="API Core"
	description="Core API Modules"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"
				
	children = [auth, modcontrol]

module = APICoreModule
