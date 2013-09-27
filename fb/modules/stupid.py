from twisted.python import log

import fb.intent as intent
from fb.modules.base import Module, require_auth, ratelimit, response
from fb.modules.quotes import parseQuoteArgs, sayQuotes

class StupidModule(Module):

	uid="stupid"
	name="Stupid"
	description="This is stupid."
	author="Tom Grochowicz (tom.grochowicz@bazaarvoice.com), Michael Pratt (michael.pratt@bazaarvoice.com)"

	listeners = {
		"sexy": {
			"keywords": r"\bex\w*\b",
			"function": "sex",
			"name": "Extra Sex",
			"description": "Someone said something sexy."
		}
	}
	commands = {
		"poopmash": {
			"keywords": "poopmash",
			"function": "poopmash",
			"name": "Poopmash",
			"description": "Returns quotes about poop."
		}
	}

	@ratelimit(30)
	@require_auth('stupid')
	@response	
	def sex(self, bot, room, user, args):
		keyword = args.group(0)
		return keyword.capitalize() +"? More like S"+keyword.upper()+"!"


	@require_auth('stupid')
	@response
	def poopmash(self, bot, room, user, args):
		nick, segment, min, max = parseQuoteArgs(args, room)
		if min is None:
			min = 3
			max = 6

		return sayQuotes(room, user, nick, "(p[o]{2,}p)|(shit)", min, max)

module = StupidModule
