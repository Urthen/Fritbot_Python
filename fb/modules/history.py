from pymongo import ASCENDING, DESCENDING

import config
from fb.db import db

import fb.intent as intent
from fb.modules.base import FritbotModule, response

class HistoryModule(FritbotModule):

	name="History"
	description="Searches the Fritbot history"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("search", self.history, self, "History Search", "Searches the Fritbot history. Say 'search help' for more info.")

	def history(self, bot, room, user, args):
		if not args:
			args = ['help']
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

module = HistoryModule()