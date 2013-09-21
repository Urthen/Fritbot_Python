import zope.interface

from fb.modules.base import IModule, response
from fb.modules.supermodule_example import subone, subtwo

class SuperModule:
	zope.interface.implements(IModule)
	name="Supermodule Test"
	description="Supermodule Test"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		subone.module().register(self)
		subtwo.module().register(self)

children = [subone, subtwo]
module = SuperModule