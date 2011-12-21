import uuid, datetime

from twisted.python import log
from twisted.internet import reactor

from fb import db
import config

_tokens = {}

def getLoginToken(application):
	token = str(uuid.uuid4())
	_tokens[token] = {'application': application, 'callbacks': []}
	log.msg("Assigned token %s for login" % token)
	reactor.callLater(config.API['login_timeout'] * 60, cancelLogin, token)
	return token

def listenForLogin(token, callback):
	if token in _tokens:
		_tokens[token]['callbacks'].append(callback)
		log.msg("Waiting for login token %s to be approved..." % token)
		return True
	else:
		log.msg("Security Alert - someone's attempted to wait for a token we aren't expecting: %s" % token)
		return False

def tokenLogin(token, user):
	if token in _tokens:
		if len(_tokens[token]['callbacks']) > 0:
			key = str(uuid.uuid4())
			for callback in _tokens[token]['callbacks']:
				callback(user, key)

			if 'authorizations' not in user.info:
				user['authorizations'] = {}
			application = _tokens[token]['application']
			user['authorizations'][application] = {'key': key, 'date': datetime.datetime.now()}
			user.save()

			log.msg("Login succeded with token %s to user %s, provided API key %s" % (token, user.uid, key))
			del _tokens[token]
			return application
		else:
			log.msg("Login failed with token %s to user %s, requestor was not listening." % (token, user.uid))
			del _tokens[token]
			return None
	else:
		log.msg("User %s attempted to login with invalid or expired token, %s" % (user.uid, token))
		return False

def cancelLogin(token):
	if token in _tokens:
		if len(_tokens[token]['callbacks']) > 0:
			for callback in _tokens[token]['callbacks']:
				callback()
		log.msg("Login token %s revoked due to timeout or cancellation" % token)
		del _tokens[token]

def revokeKey(user, application):
	if application in user['authorizations']:
		del user['authorizations'][application]
		user.save()
		return True
	else:
		return False
