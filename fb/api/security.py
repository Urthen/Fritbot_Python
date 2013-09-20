import uuid, datetime

from twisted.python import log
from twisted.internet import reactor

from fb import db
from fb.config import cfg

_tokens = {}

def getLoginToken(application):
	token = str(uuid.uuid4())
	_tokens[token] = {'application': application, 'callbacks': []}
	log.msg("Assigned token %s for login" % token)
	reactor.callLater(cfg.api.login_timeout * 60, cancelLogin, token)
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
				user['authorizations'] = []
			application = _tokens[token]['application']
			user['authorizations'].append({'app': application, 'key': key, 'date': datetime.datetime.now()})
			user.save()

			log.msg("Login succeded with token %s to user %s, provided API key %s" % (token, user.uid, key))
			del _tokens[token]
			return application
		else:
			log.msg("Login failed with token %s to user %s, requestor was not listening." % (token, user.uid))
			del _tokens[token]
			return None
	else:
		print("User %s attempted to login with invalid or expired token, %s" % (user.uid, token))
		return False

def cancelLogin(token):
	if token in _tokens:
		if len(_tokens[token]['callbacks']) > 0:
			for callback in _tokens[token]['callbacks']:
				callback()
		log.msg("Login token %s revoked due to timeout or cancellation" % token)
		del _tokens[token]

def revokeKey(user, application=None, key=None):
	newauths = user['authorizations']
	removed = False
	for k in user['authorizations']:	
		if k['key'] != key and k['app'] != application:
			newauths.append(k)
		else:
			removed = True
	user['authorizations'] = newauths
	user.save()
	return removed

def getKeyInfo(key):
	user = db.db.users.find_one({'authorizations.key': key})
	if user is None:
		return None

	data = None
	for k in user['authorizations']:	
		if k['key'] == key:
			data = k
			break

	output = {'nick': user['nick'],
		'date': str(data['date']),
		'userid': user['resource'],
		'app': data['app']
	}

	return output
