from fb.modules.base import Module
from fb.modules.facts import api, commands

class FactsModule(Module):

	uid="facts"
	name="Facts"
	description="Responds to other users' chats with super A+ userful factoids."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"
				
	children = [api, commands]
	
module = FactsModule
