import zope.interface

from fb.db import db
import fb.intent as intent
import fb.modules.base as base
from twisted.python import log

class NicknameModule:
	zope.interface.implements(base.IModule)

	name="Nicknames"
	description="Simple functions to manipulate the name of the bot or the user"
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand(['become', 'ghost', 'you are', 'your (nick)?name is', 'nickname'], self.ghost, self, "Change Bot Nickname", "Change the nickname of the bot in the current room with 'become SuperBot'.")
		intent.service.registerCommand(['identify'], self.getName, self, "View Bot Nickname", "View the nickname of the bot in the current room with 'identify'.")
		intent.service.registerCommand(['i am', 'my (nick)?name is', 'call me'], self.callMe, self, "Change User Nickname", "Change the bot's nickname of the user with 'my name is Awesome Dude'.")
		intent.service.registerCommand(['what((s)| is) my (nick)?name', 'who am i'], self.myname, self, "Get User Nickname", "Responds with what the bot calls the user.")

	@base.room_only
	@base.response
	def ghost(self, bot, room, user, args):
		newnick = ' '.join(args)

		if len(newnick) < 1:
			return "You can't call me nothing!"

		if room is None:
			return "This isn't a chat room!"

		logstatement = "Changed nick from {0} to {1}".format(room['nick'], newnick)
		log.msg(logstatement)
		try:
			room.setNick(newnick)
			return "Behold! By the power of {0}, I am now {1}!".format(user['nick'], newnick)
		except Exception as e:
			log.msg(e)
			return "Something went haywire, there's probably already someone by that name!"

	@base.room_only
	@base.response
	def getName(self, bot, room, user, args):

		if room is None:
			return "This isn't a chat room!"

		try:
			return "My name is {0}.".format(room['nick'])
		except:
			return "Something went haywire, I don't understand what's going on!!"

	@base.response
	def callMe(self, bot, room, user, args):
		
		newnick = ' '.join(args)
		if len(newnick) < 1:
			return "I can't call you nothing!"

		if newnick == user['nick']:
			return "Thats your name already, {0}!".format(newnick)

		existing = db.db.users.find_one({"nick": newnick})

		if existing is not None:
			return "Sorry, we've already got someone by that name: {0}".format(existing["resource"])
		
		user['nick'] = newnick
		user.save()

		return "Ok then, I now know you as {0}.".format(newnick)

	@base.response
	def myname(self, bot, room, user, args):
		print type(user['nick'])
		print user['nick']
		return "Your name is {0}".format(user['nick'])

module = NicknameModule()