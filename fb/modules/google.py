#Searching for the YAY!

import json, urllib

from twisted.python import log

import fb.intent as intent
from fb.modules.base import Module, require_auth, response
from fb.config import cfg


_gdata_supported = False
try:
	import gdata.youtube.service
	_gdata_supported = True
except:
	log.msg("gdata.youtube.service not found, did you install the python google data api library? Running without it for now.")

class GoogleSearchModule(Module):

	uid="google"
	name="Google Search"
	description="Functionality for searching Google Web and YouTube"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	gdata_supported = _gdata_supported

	commands = {
		"google": {
			"keywords": "google",
			"function": "google",
			"name": "Google Search",
			"description": "Returns Google 'I'm feeling lucky' result. Use 'google more' to return multiple ranked results."
		},
		"youtube": {
			"keywords": "youtube",
			"function": "youtube",
			"name": "Youtube Search",
			"description": "Returns YouTube search result. Use 'youtube more' to return up to 5 ranked results."
		}
	}

	@require_auth('search', "Search isn't allowed here!", False)
	@response
	def google(self, bot, room, user, args):
		if args[0] == "more":
			more = True
			args = args[1:]
		else:
			more = False
		query = urllib.urlencode({'q': ' '.join(args)})
		url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
		search_response = urllib.urlopen(url)
		search_results = search_response.read()
		results = json.loads(search_results)
		data = results['responseData']

		if len(data['results']):
			if more:
				msg = ''
				num = 1
				for result in data['results']:
					msg += u"{0}: {1} - {2}\n".format(str(num), result['titleNoFormatting'], result['url'])
					num += 1

				msg += u"For more results, see %s" % data['cursor']['moreResultsUrl']
			else:
				msg = u"{0} - {1}\n".format(data['results'][0]['titleNoFormatting'], data['results'][0]['url'])
		else:
			msg = u"Sorry, {0}, Google doesn't seem to know anything about that.".format(user['nick'])
		return msg

	@require_auth('search', "Search isn't allowed here!", False)
	@response
	def youtube(self, bot, room, user, args):
		if not self.gdata_supported:
			return u"Google data API not installed, contact your bot admin."

		if args[0] == "more":
			more = True
			args = args[1:]
		else:
			more = False

		yt_service = gdata.youtube.service.YouTubeService()
		query = gdata.youtube.service.YouTubeVideoQuery()
		
		try:
			if cfg.google.racy:
				query.racy = "include"
			else:
				query.racy = "exclude"
		except:
			query.racy = "exclude"		    
	
		query.vq = ' '.join(args)
		feed = yt_service.YouTubeQuery(query)

		if len(feed.entry):
			if more:
				lines = []
				for num in xrange(0, 5):
					lines.append('{0}: {1} - {2}'.format(num + 1, feed.entry[num].media.title.text, feed.entry[num].media.player.url))

				return '\n'.join(lines)
			else:
				return "{0} - {1}".format(feed.entry[0].media.title.text, feed.entry[0].media.player.url)
		
		return "Sorry {0}, I can't find any videos for that query.".format(user['nick'])

module = GoogleSearchModule
