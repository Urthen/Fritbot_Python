import re, random
from pymongo import Connection, errors as PyMongoErrors

rooms = ['offtopic', 'design', 'support_analyst']

connection = Connection()
db = connection["fritbot"]
roomsreturned = db.rooms.find({'name': {'$in': rooms}})
roomids = []
for room in roomsreturned:
	roomids.append(room['_id'])

log = db.history.find({'room': {'$in': roomids}})

stats = {}

splitter = re.compile("([,\.!\?-_:;]+( +|$))|(-)|([^,!\?\-_:;\(\)\" ]+)")

END = "__end__"

lines = log.count()
done = 0
print "Reading {0} lines".format(lines)

for line in log:
	history = [""]
	text = line["body"].lower()
	#print "*** " + text
	segments = map(lambda x: ''.join(x), splitter.findall(text))
	segments.append(END)

	for segment in segments:
		#print "** " + segment
		for delay in range(len(history)):
			word = history[delay]
			if word not in stats:
				stats[word] = {}
			if segment not in stats[word]:
				stats[word][segment] = [0, 0, 0]
			
			stats[word][segment][delay] += 1
			#print u"{0}-{1}->{2}: {3}".format(word, delay, segment, stats[word][segment][delay])
		history.insert(0, segment)
		history = history[0:3]

	done += 1
	if done % 2500 == 0:
		print "{0}/{1}".format(done, lines)


done = 0
print "Clearing...."
db.markov.remove({})
print "Writing {0} words.".format(len(stats))
for wordFrom in stats:
	statsFrom = stats[wordFrom]
	for wordTo in statsFrom:
		statsTo = statsFrom[wordTo]
		doc = {"from": wordFrom, "to": wordTo, "stats": statsTo}
		db.markov.insert(doc)
	
	done += 1
	if done % 2500 == 0:
		print "{0}/{1}".format(done, len(stats))

print doc