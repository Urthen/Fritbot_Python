import random, datetime

from twisted.python import log
from twisted.internet import reactor

from fb import db
from fb.config import cfg

def getKey(application, user):
	key = '%030x' % random.randrange(16**30)
	user['authorizations'].append({'app': application, 'key': key, 'date': datetime.datetime.now()})
	user.save()

	log.msg("Assigned key {0} to user {1}, application {2}".format(key, application, user['nick']))
	return key

def revokeKey(user, application=None, key=None):
	newauths = []
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
