#!/bin/python
#temporary script to copy facts from temporary format, not neccesary moving forward

import pymongo
import datetime

connection = pymongo.Connection()

db = connection['fritbot']

oldformat = db.intents.find()

for fact in oldformat:
	createdtime = datetime.datetime.strptime(fact['created'][0], '%Y-%m-%d %H:%M:%S')
	factoids = []

	for factoid in fact['actions']:
		new_factoid = {
			'created': factoid['created'],
			'author': factoid['author'],
			'reply': factoid['list'][0]['say']
		}
		factoids.append(new_factoid)

	new_fact = {
		'created': createdtime,
		'factoids': factoids,
		'count': 0,
		'triggers': fact['triggers']
	}

	db.facts.insert(new_fact)