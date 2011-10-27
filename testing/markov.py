import re, random
from pymongo import Connection, errors as PyMongoErrors

connection = Connection()
db = connection["fritbot"]
history = db.history
markov = db.markov

log = history.find()

stats = {}

splitter = re.compile("([,\.!\?-_:;]+( +|$))|(-)|([^,!\?\-_:;\(\)\" ]+)")
punc = re.compile("[,\.!\?-_:;]( +|$)")

END = "__end__"
SUM = "__sum__"

for line in log:
	last = ""
	text = line["body"].lower()
	segments = map(lambda x: ''.join(x), splitter.findall(text))
	segments.append(END)

	for segment in segments:
		if last not in stats:
			stats[last] = {}
		if segment not in stats[last]:
			stats[last][segment] = 1
		else:
			stats[last][segment] += 1

		#print last, segment, stats[last][segment]
		last = segment
		
for stat in stats.values():
	stat[SUM] = reduce(lambda a, b: a + b, stat.values())

state = ""
output = []
while len(output) < 20:
	stat = stats[state]
	total = stat[SUM]
	rand = random.randrange(total)
	#print state, total, rand
	for seg in stat:
		if seg == SUM:
			continue
		rand -= stat[seg]
		#print seg, stat[seg], rand
		if rand <= 0:
			break
	if seg == END:
		if len(output) > 5:
			break
		else:
			state = ""
	else:
		output.append(seg)
		state = seg

string = ""
for out in output:
	if punc.match(out):
		string += out.rstrip()
	else:
		string += " " + out

print string.lstrip()