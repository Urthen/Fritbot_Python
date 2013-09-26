from __future__ import division
import re, random, math

from twisted.internet import reactor

import fb.intent as intent
from fb.modules.base import Module, ratelimit, require_auth, response

from fb.db import db

class MarkovModule(Module):

	uid="markov"
	name="Markov Chains"
	description="Adds babbling functionality by randomly selecting old snippets of text from historical conversations."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	punc = re.compile("[,\.!\?-_:;]( +|$)")

	END = "__end__"
	
	maximum = 1

	commands = {
		"babble": {
			"keywords": "babble",
			"function": "babble",
			"name": "Babble",
			"description": "Say a randomly generated phrase"
		}
	}

	def doMarkov(self, room, user):
		state = [""]
		cache = {}
		output = []
		while len(output) < 20:	
			segments = {}
			total = 0.
			for delay in range(min(len(state), self.maximum)): #len(state)):
				if state[delay] not in cache:
					cursor =  db.db.markov.find({'from': state[delay]})
					cache[state[delay]] = {}
					data = cache[state[delay]]
					for word in cursor:
						data[word['to']] = word['stats']
				else:		
					data = cache[state[delay]]

				for word in data:
					if delay < 3:
						power = data[word][delay] / math.pow(delay + 1, 2)
					if word not in segments:
						segments[word] = power
					else:
						segments[word] += power
					total += power

			rand = random.randrange(math.floor(total))
			#print state, total, rand
			for seg in segments:
				rand -= segments[seg] 
				#print seg, stat[seg], rand
				if rand <= 0:
					break
			if seg == self.END:
				if len(output) > 6:
					break
				else:
					state.insert(0, "")
			else:
				output.append(seg)
				state.insert(0, seg)

		string = ""
		for out in output:
			if self.punc.match(out):
				string += out.rstrip()
			else:
				string += " " + out

		if room is not None:
			room.send(string.lstrip())
		else:
			user.send(string.lstrip())

	@require_auth('babble', "I can't babble here!", False)
	@ratelimit(4, "Slow your roll! I need time for my creative genius!", False)
	def babble(self, bot, room, user, args):
		reactor.callLater(0, self.doMarkov, room, user)
		return True

module = MarkovModule
