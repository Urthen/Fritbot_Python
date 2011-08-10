#Nickname Functionsies

from fb.db import db

def ghost(bot, room, user, args):
    newnick = ' '.join(args)

    if len(newnick) < 1:
        return "You can't call me nothing!"

    if room is None:
        return "This isn't a chat room, dumbass!"

    msg = "Changed nick from {0} to {1}".format(room['nick'], newnick)
    undo = {'function': undoGhost, 'original': room['nick'], 'message': msg}

    try:
        room.setNick(newnick)
        bot.addUndo(room, user, undo)
        return "Behold! By the power of {0}, I am now {1}!".format(user['nick'], newnick)
    except:
        return "Something went haywire, there's probably already someone by that name!"

def undoGhost(bot, room, user, args):
    try:
        room.setNick(args['original'])
        return True, "Ok, I'm now back to {0}.".format(args['original'])
    except:
        return False, "Someone's stolen my name! I can't go back right now!"
        

def callMe(bot, room, user, args):
    
    newnick = ' '.join(args)
    if len(newnick) < 1:
        return "I can't call you nothing!"

    existing = db.db.users.find_one({"nick": newnick})

    if existing is not None:
        return "Sorry mate, we've already got someone by that name: {0}".format(existing["resource"])

    
    user['nick'] = newnick
    user.save()

    return "Ok then, I now know you as {0}.".format(newnick)