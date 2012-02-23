#Searching for the YAY!

import json, urllib

from twisted.python import log

import fb.intent as intent
from fb.modules.base import FritbotModule, response

class TwitterModule(FritbotModule):

	name="Twitter"
	description="Functionality for searching Twitter"
	author="Kyle Varga (kyle.varga@bazaarvoice.com)"

	gdata_supported = False

	def register(self):
		#intent.service.registerCommand("google", self.google, self, "Google Search", "Returns Google 'I'm feeling lucky' result. Use 'google more' to return multiple ranked results.")
		#intent.service.registerCommand("youtube", self.youtube, self, "YouTube Search", "Returns YouTube search result. Use 'youtube more' to return up to 5 ranked results.")
		intent.service.registerCommand("twitter", self.twitter, self, "Twitter", "twitter")

	@response
	def twitter(self, bot, room, user, args):

		query = urllib.urlencode({'q':' '.join(args)})
		url = 'http://search.twitter.com/search.json?%s' % query
		twitter_response = urllib.urlopen(url)
		twitter_results = twitter_response.read()
		results = json.loads(twitter_results)
		data = results

		if len(data['results']):
			msg = 'Twitter results for ' + data['query'] + ':\n'
			for result in data['results']:
				msg += '@' + result['from_user'] + ': ' + result['text'] + '\n'
		else:
			msg = "Sorry, {0}, Twitter doesn't seem to know anything about that.".format(user['nick'])
		return msg

module = TwitterModule()


