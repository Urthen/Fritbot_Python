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
        if len(args) > 0:
            uas = args[0]
        else:
            return 'no auth string passed'
        return uas[32:].decode('hex')
            	
module = UASModule()