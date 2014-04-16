import datetime

from twisted.python import log
from twisted.internet import reactor

import fb.intent as intent
import fb.modules.base as base
from fb.modules.util import getUser
from fb.db import db
from fb.config import cfg
from fb.modulecontrol import moduleLoader

class CoreCommandsModule(base.Module):

	uid="chat_core.commands"	
	name="Core Commands"
	description="Core Fritbot Commands, minimum functionality."
	author="Michael Pratt (michael.pratt@bazaarvoice.com)"

	commands = {
		
		"allow": {
			"keywords": "allow",
			"function": "allow",
			"name": "Allow",
			"description": "(admin) Allows functionality in room",
			"core": True
		},
		"disallow": {
			"keywords": "disallow",
			"function": "disallow",
			"name": "Disallow",
			"description": "(admin) Disallow funcionality in a room",
			"core": True
		},
		"auths": {
			"keywords": "auths",
			"function": "auths",
			"name": "Authorizations",
			"description": "Lists available functionaity in a room",
			"core": True
		},
		"shutup": {
			"keywords": ["shut ?up", "(be )?quiet"],
			"function": "quiet",
			"name": "Shut Up",
			"description": "Shuts up the bot for non-core functions for 5 minutes",
			"core": True
		},
		"comeback": {
			"keywords": "come back",
			"function": "unquiet",
			"name": "Come Back",
			"description": "Allows the bot to talk again if shut up",
			"core": True
		},
		"shutdown": {
			"keywords": "shut ?down",
			"function": "shutdown",
			"name": "Shut Down",
			"description": "(admin) Turns off the bot entirely",
			"core": True
		},
		"ignore": {
			"keywords": ["ignore", "ban"],
			"function": "ignore",
			"name": "Ignore",
			"description": "(admin) Sets the bot to ignore a user",
			"core": True
		},
		"join": {
			"keywords": ['join', 'enter', 'go ?(to)?'],
			"function": "join",
			"name": "Join Room",
			"description": "Joins designated room with 'join roomname', optionally with nickname as 'join roomname FunBotName'",
			"core": True
		},
		"leave": {
			"keywords": ['get out', 'leave'],
			"function": "leave",
			"name": "Leave",
			"description": "Leaves current room, or leaves another room with 'leave roomname'",
			"core": True
		}
	}

	@base.response
	def join(self, bot, room, user, args):
		'''Joins a room.'''

		if len(args) == 0:
			return "Join where?"

		join = args.pop(0)
		nick = cfg.bot.name

		if len(args) >= 2:
			if args[0] == "as":
				nick = args[1]

		bot.joinRoom(join, nick)
		return "Ok, I've jumped into {0}!".format(join)

	def leave(self, bot, room, user, args):
		'''Leaves a room.'''
		if len(args):
			if args[0] in bot.rooms:
				room = bot.rooms[args[0]]
			else:
				if room is not None:
					room.send("I'm not in {0}...".format(args[0]))
				else:
					user.send("I'm not in {0}...".format(args[0]))
				return True

		elif room is None:
			user.send("We're talking privately, I can't leave!")
			
		room.send("Bye!")
		bot.leaveRoom(room)
		return True

	@base.admin
	@base.room_only
	@base.response
	def allow(self, bot, room, user, args):
		if len(args) < 1:
			return "Must specify a permission..."
		else:
			auths = set(room["auths"]) | set(args)
			room["auths"] = list(auths)
			room.save()

			return "Ok, allowing the following authorizations: {0}".format(', '.join(args))

	@base.admin
	@base.room_only
	@base.response
	def disallow(self, bot, room, user, args):
		if len(args) < 1:
			return "Must specify a permission..."
		else:
			auths = set(room["auths"]) - set(args)
			room["auths"] = list(auths)
			room.save()

			return "Ok, disallowing the following authorizations: {0}".format(', '.join(args))

	@base.room_only
	@base.response
	def auths(self, bot, room, user, args):
		return "I currently have the following authorizations for the {0} room: {1}".format(room.uid, ', '.join(room["auths"]))

	@base.room_only
	@base.response
	def quiet(self, bot, room, user, args):
		'''Squelches the bot for the given room.'''

		room["squelched"] = datetime.datetime.now() + datetime.timedelta(minutes=5);
		room.save()
		return "Shut up for 5 minutes."

	@base.room_only
	@base.response
	def unquiet(self, bot, room, user, args):

		room["squelched"] = datetime.datetime.now() - datetime.timedelta(minutes=5);
		room.save()
		return "And we're back."

	@base.admin
	@base.response
	def shutdown(self, bot, room, user, args):
		log.msg("Shutting down by request from {0}.".format(user['nick']))
		bot.shutdown()
		return "Ok, shutting down momentarily."

	@base.admin
	@base.response
	def ignore(self, bot, room, user, args):
		if len(args):
			reason = "Check your behavior."
			if len(args) > 1:
				reason = " ".join(args[1:])
			victim = getUser(args[0])
			if len(victim):
				victim = victim[0][0]
				if victim.get("banned", False):
					victim["banned"] = False
					db.users.update({"_id": victim["_id"]}, victim)
					return "{0} has been unbanned.".format(victim["nick"])
				else:
					victim["banned"] = reason					
					db.users.update({"_id": victim["_id"]}, victim)
					return "{0} has been banned.".format(victim["nick"])
			else:
				return "Can't find a user by the name {0}".format(args[0])
		else:
			banned = db.users.find({"banned": True})
			outlist = ", ".join([u["nick"] for u in banned])
			return "Banned Users: " + outlist

module = CoreCommandsModule