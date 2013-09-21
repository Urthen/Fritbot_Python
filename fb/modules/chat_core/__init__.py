from fb.modules.base import Module
from fb.modules.chat_core import commands, help, security, modcontrol

class ChatCoreModule(Module):

	uid="chat_core"
	name="Chat Core"
	description="Core Chat Modules"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"
				
	children = [commands, help, security, modcontrol]

module = ChatCoreModule
