import fb.intent as intent
from fb.modules.base import FritbotModule, response

class UASModule(FritbotModule):
    name="UserAuthString"
    description="Functions for user authentication strings"
    author="Kyle Varga (kyle.varga@bazaarvoice.com)"

    def register(self):
        intent.service.registerCommand("decode", self.decodeUAS, self, "Decode Auth String", "Decodes Auth Strings.")
        
    @response
    def decodeUAS(self, bot, room, user, args):
        if room.uid == 'offtopic':
            return 'WTF ARE YOU DOING?! THIS IS OFF TOPIC!!!'
        if len(args) > 0:
            uas = args[0]
        else:
            return 'no auth string passed'
        
        
        try:
            returnStr = uas[32:].decode('hex')
        except:
            returnStr = 'Not a valid user authentication string'        
        
        if len(returnStr) == 0:
            returnStr = 'Not a valid user authentication string'        
        
        return returnStr            	
module = UASModule()