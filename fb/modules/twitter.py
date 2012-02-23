#Searching Twitter

import json, urllib
from fb.db import db

from twisted.python import log

import fb.intent as intent
from fb.modules.base import FritbotModule, response

class TwitterModule(FritbotModule):

	name="Twitter"
	description="Functionality for searching Twitter"
	author="Kyle Varga (kyle.varga@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("twitter", self.twitter, self, "Twitter Search", "Returns all results from Twitter Search API")
		intent.service.registerCommand("twitterclear", self.twitterClear, self, "Twitter Clear", "Clears recent history for all or specific query")

	@response
	def twitter(self, bot, room, user, args):
		query = urllib.urlencode({'q':' '.join(args)})
		existing = db.db.twittersearch.find_one({"query": query})
		url = "http://search.twitter.com/search.json?"
		
		# Logic to determine if we have searched this query before
		# TODO: Make these expire after X hours or X days?
		if existing is None:
			print 'Never searched for this before.. searching now..'
			msg = 'First time I`ve searched for this before...\n' 
		else:
			print 'Searching now...'
			msg = 'I`ve searched for this before. Only showing recent results:\n'
			since = str(existing['max_id'])
			url = 'http://search.twitter.com/search.json?since_id=' + since + '&'
		
		url += query

		twitter_response = urllib.urlopen(url)
		twitter_results = twitter_response.read()
		results = json.loads(twitter_results)
		data = results
		since = results['max_id']

		# Remove current search history, insert latest
		db.db.twittersearch.remove({"query": query})
		db.db.twittersearch.insert({"query": query, "max_id": since});
		
		if len(data['results']):
			for result in data['results']:
				msg += '\t@' + result['from_user'] + ': ' + result['text'] + '\n'
		else:
			if existing is not None:
				msg = "Slow your roll {0}, Twitter doesn't have anything new yet.".format(user['nick'])
			else:
				msg = "Sorry, {0}, Twitter doesn't know what you are talking about.".format(user['nick'])
		return msg

	@response
	def twitterClear(self, bot, room, user, args):
		db.db.twittersearch.remove()
		return 'Removed all twitter search history'

	

module = TwitterModule()


