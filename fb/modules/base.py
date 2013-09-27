from datetime import datetime, timedelta

from fb.audit import log
from fb.api.core import api
import fb.intent

import zope.interface
 	
def response(f):
	def responder(self, bot, room, user, args):
		out = f(self, bot, room, user, args)

		if out is None:
			return False

		if type(out) == type(u'') or type(out) == type(''):
			if room is not None:
				room.send(out)
			else:
				user.send(out)
			return True

		log.msg("Invalid type returned by function wrapped by @response: {0} - {1}".format(out, type(out)))
		return False

	return responder

def admin(f):
	def admincheck(self, bot, room, user, args):
		if user.admin:
			return f(self, bot, room, user, args)
		else:
			log.msg("User {0} ({1}) attempted to run a function without authorization.".format(user['nick'], user.uid))
			user.send("That function requires you to be an administrator. You aren't.")
			return True

	return admincheck

def room_only(f):
	def roomcheck(self, bot, room, user, args):
		if room is not None:
			return f(self, bot, room, user, args)
		else:
			user.send("That function only works in a room.")
			return True

	return roomcheck

def user_only(f):
	def roomcheck(self, bot, room, user, args):
		if room is None:
			return f(self, bot, room, user, args)
		else:
			user.send("That function only works directly with me, not in a room. Why don't you try it now?")
			return True

	return roomcheck

def ratelimit(rate, message=None, passthrough=True):	
	def ratelimitgen(f):
		name = f.__name__
		def ratelimited(self, bot, room, user, args):
			if room:
				if name in room.ratelimit and room.ratelimit[name] > datetime.now():
					log.msg("Almost executed {0} in {1} but it was too soon.".format(name, room))
					if message:
						user.send(message)
					return not passthrough
				else:
					room.ratelimit[name] = datetime.now() + timedelta(seconds=rate)
					log.msg("Won't execute {0} again until {1}.".format(name, room.ratelimit[name]))
					return f(self, bot, room, user, args)
			else: #user case
				return f(self, bot, room, user, args) 

		return ratelimited
	return ratelimitgen

def require_auth(permission, message=None, passthrough=True):
	def reqauthgen(f):
		def authrequired(self, bot, room, user, args):
			if room is None or room.allowed(permission):
				return f(self, bot, room, user, args)
			elif message:
				user.send(message.format(room['name']) + "\nRequired authorization: " + permission)			
			return not passthrough
		return authrequired
	return reqauthgen

class Module():
	uid="module_filename"
	name="Module Name"
	description="Module Description"
	author="Module Author <author@example.com>"

	children = []
	listeners = {}
	commands = {}
	apis = {}

	def __init__(self):
		self._children = {}
		for child in self.children:
			try:
				self._children[child.__name__] = child.module()
			except:
				log.msg("Error loading %s child module %s:" % (self.uid, child.__name__), log.ERROR)
				raise

	def register(self):
		"""Functionality to register the module with the intent & api services."""

		for key, command in self.commands.items():
			isCore = False

			if 'core' in command and command['core']:
				isCore = True

			try:
				fb.intent.service.registerCommand(command['keywords'], getattr(self, command['function']), self.uid + ":command." + key, isCore)
			except:
				log.msg("Error registering %s command %s:" % (self.uid, key), log.ERROR)
				raise

		for key, listener in self.listeners.items():
			try:
				fb.intent.service.registerListener(listener['keywords'], getattr(self, listener['function']), self.uid + ":listener." + key)
			except:
				log.msg("Error registering %s listener %s:" % (self.uid, key), log.ERROR)
				raise

		for path, module in self.apis.items():
			if type(module) == type(()):
				api.registerModule(path, module[0], module[1])
			else:
				api.registerModule(path, module)

		for name, child in self._children.items():
			try:
				child.register()
			except:
				log.msg("Error registering %s child module %s:" % (self.uid, name), log.ERROR)
				raise

	def unregister(self):
		"""Functionality to unload the module from the intent & api services."""

		for child in self._children.values():
			child.unregister()

		for path in self.apis.keys():
			api.removeModule(path)

		for key in self.listeners.keys():
			fb.intent.service.unregisterCommand(self.uid + ":listener." + key)

		for key in self.commands.keys():
			fb.intent.service.unregisterCommand(self.uid + ":command." + key)

