from fb.modules.base import Module, response
from fb.modules.supermodule_example import subone, subtwo

class SuperModule(Module):

	uid="supermodule_example"
	name="Supermodule Test"
	description="Supermodule Test"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	children = [subone, subtwo]
	
module = SuperModule