#Searching for the YAY!

import json, urllib, xmlrpclib

from twisted.python import log

from pymongo import ASCENDING, DESCENDING

import config
from fb.db import db

gdata_supported = False

try:
	import gdata.youtube.service
	gdata_supported = True
except:
	log.msg("gdata.youtube.service not found, did you install the python google data api library? Running without it for now.")


# def google(bot, room, user, args):
# 	if args[0] == "more":
# 		more = True
# 		args = args[1:]
# 	else:
# 		more = False
# 	query = urllib.urlencode({'q': ' '.join(args)})
# 	url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
# 	search_response = urllib.urlopen(url)
# 	search_results = search_response.read()
# 	results = json.loads(search_results)
# 	data = results['responseData']

# 	if len(data['results']):
# 		if more:
# 			msg = ''
# 			num = 1
# 			for result in data['results']:
# 				msg += u"{0}: {1} - {2}\n".format(str(num), result['titleNoFormatting'], result['url'])
# 				num += 1

# 			msg += "For more results, see %s" % data['cursor']['moreResultsUrl']
# 		else:
# 			msg = u"{0} - {1}\n".format(data['results'][0]['titleNoFormatting'], data['results'][0]['url'])
# 	else:
# 		if room is not None and room.allowed('mean'):
# 			msg = "Sorry, {0}, the internet has no idea what nonsense you are spouting.".format(user['nick'])
# 		else:
# 			msg = "Sorry, {0}, Google doesn't seem to know anything about that.".format(user['nick'])
# 	return msg

# def youtube(bot, room, user, args):
# 	if not gdata_supported:
# 		return "Google data API not installed, contact your {0} admin.".format(config.CONFIG['name'])

# 	if args[0] == "more":
# 		more = True
# 		args = args[1:]
# 	else:
# 		more = False

# 	yt_service = gdata.youtube.service.YouTubeService()
# 	query = gdata.youtube.service.YouTubeVideoQuery()
# 	if config.CONFIG["racy"]:
# 		query.racy = "include"
# 	else:
# 		query.racy = "exclude"
# 	query.vq = ' '.join(args)
# 	feed = yt_service.YouTubeQuery(query)

# 	if len(feed.entry):
# 		if more:
# 			lines = []
# 			for num in xrange(0, 4):
# 				lines.append('{0}: {1} - {2}'.format(num + 1, feed.entry[num].media.title.text, feed.entry[num].media.player.url))

# 			return '\n'.join(lines)
# 		else:
# 			return "{0} - {1}".format(feed.entry[0].media.title.text, feed.entry[0].media.player.url)
	
# 	if room is not None and room.allowed('mean'):
# 		return "Whatever crazy thing {0} wanted to watch isn't available.".format(user['nick'])
# 	else:
# 		return "Sorry {0}, I can't find any videos for that query.".format(user['nick'])

def confluence(bot, room, user, args):
	if not config.CONFLUENCE["enabled"]:
		return "Confluence search is not enabled, contact your {0} admin.".format(config.CONFIG['name'])

	more = False
	results = 1
	if args[0] == "more":
		more = True
		results = 3
		args = args[1:]

	s = xmlrpclib.Server(config.CONFLUENCE["url"])
	try:
		token = s.confluence1.login(config.CONFLUENCE["username"], config.CONFLUENCE["password"])
	except xmlrpclib.Fault:
		return "Login failure, cannot search Confluence. Contact your {0} admin.".format(config.CONFIG['name'])

	search = s.confluence1.search(token, ' '.join(args), results)

	if len(search) > 0:
		if more:
			lines = []
			line = 1
			for l in search:
				lines += "{0}: {1} - {2}".format(line, l['title'], l['url'])
			return '\n'.join(lines)
		else:
			return "{0} - {1}".format(search[0]['title'], search[0]['url'])
	else:
		return "Sorry {0}, Confluence reports no results for that query.".format(user['nick'])


def history(bot, room, user, args):
	if args[0] == "expand":
		if not hasattr(user, 'search'):
			user.send("You have to start a search before you can extend a result!")
		args = args[1:]

		back = 0
		fore = 0

		try:
			number = int(args[0])
			assert(number > 0)
		except:
			user.send("Invalid number {0}".format(args[0]))
			return None

		for arg in args[1:]:
			if arg[0] != '-':
				try:
					fore = int(arg[1:])
				except:
					user.send("Invalid foreward {0}".format(arg))
					return None
			else:
				try:
					back = int(arg[1:])
				except:
					user.send("Invalid backward {0}".format(arg))
					return None

		queryResult = {
			'body': {'$regex': user.search['text'], '$options': 'i'},
			'command': False
		}
		if user.search['room'] is not None:
			queryResult['room'] = user.search['room']['_id']

		result = db.db.history.find(queryResult).limit(1).sort('date', DESCENDING).skip(number - 1)
		if result.count() == 0:
			user.send("Hrm, I can't seem to get that result. Is that a valid number?")
			return
		date = result[0]['date']

		out = []
		resultForward = []
		resultBackward = []

		if fore > 0:
			queryForward = queryResult.copy()
			queryForward['date'] = {'$gt': date}
			del(queryForward['body'])

			rForward = db.db.history.find(queryForward).sort('date', ASCENDING).limit(fore)
			for r in rForward:
				resultForward.append('<{0}, {2}>: {1}'.format(r['user']['nick'], r['body'], r['date'].strftime("%m/%d/%y, %I:%M %p")))

		if back > 0:
			queryBackward = queryResult.copy()
			queryBackward['date'] = {'$lt': date}
			del(queryBackward['body'])

			rBackward = db.db.history.find(queryBackward).sort('date', DESCENDING).limit(back)
			for r in rBackward:
				resultBackward.insert(0, '<{0}, {2}>: {1}'.format(r['user']['nick'], r['body'], r['date'].strftime("%m/%d/%y, %I:%M %p")))

		out.extend(resultBackward)
		out.append(('<{0}, {2}>: {1}'.format(result[0]['user']['nick'], result[0]['body'], result[0]['date'].strftime("%m/%d/%y, %I:%M %p"))))
		out.extend(resultForward)

		if room is not None:
			room.send('\n'.join(out))
		else:
			user.send('\n'.join(out))
 
	elif args[0] == "help":
		user.send("Searching is done entirely through direct communication, since it can get quite spammy.\n" +
			"By now, you've undoubtably figured out that 'search <room name> <some query>' initiates the search. You can use Regular Expressions in the searching.\n" +
			"If any of the results look promising, you can do 'search expand <number> <expansion>' and that will show you more context about that individual result.\n" +
			"<expansion> can be how far you would like to look forwards or backwards.\n" +
			"'search expand 2 +20' will return the search result and the next 20 lines said in that room." +
			"'search expand 1 +10 -5' will return from 5 lines back to 10 lines forward.\n" +
			"Finally, if you would like to output the results, use '>room search expand <number> <expansion>' and it will report to the indicated room the result of the above."
		)
	else:
		stroom = args[0]
		more = False
		start_new = False
		if stroom == "more":
			more = True
		
		text = ' '.join(args[1:])

		if stroom in ['any', 'anywhere', 'all', '*', '%']:
			room = None
		elif not more and stroom != 'here':
			if stroom in bot.rooms:
				room = bot.rooms[stroom]
			else:
				return "Sorry, I'm not in '{0}' and can't search it unless I am.".format(stroom)

		if more:
			if not hasattr(user, 'search'):
				user.send("You have to start a search before you can get more...")
				return
			else:
				user.search['skip'] += 10
				text = user.search['text']
				room = user.search['room']
		else:
			user.search = {'text': text, 'skip': 0}
			if room is not None:
				user.search['room'] = room
			else:
				user.search['room'] = None
		
		query = {
			'body': {'$regex': text, '$options': 'i'},
			'command': False
		}
		if room is not None:
			query['room'] = room['_id']

		history = db.db.history.find(query).sort('date', DESCENDING).limit(10).skip(user.search['skip'])
		
		num = user.search['skip'] + 1
		lines = []
		if num == 1:
			if user.search['room'] is not None:
				lines.append("Searched {0} for {1}:".format(user.search['room'].uid, user.search['text']))
			else:
				lines.append("Searched all history for {0}:".format(user.search['text']))
			lines.append("(Type 'search help' for more information)")
		for item in history:
			lines.append('#{0} - <{1}, {3}>: {2}'.format(num, item['user']['nick'], item['body'], item['date'].strftime("%m/%d/%y, %I:%M %p")))
			num += 1

		count = history.count() - user.search['skip'] - 10
		if count > 0:
			lines.append("{0} more results, type 'search more' to view.".format(count))

		if num > 1:
			user.send('\n'.join(lines))
		else:
			if more:
				user.send("No more!")
			else:
				user.send("I can't find any history of '{1}'.".format(user['nick'], text))