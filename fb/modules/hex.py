import fb.intent as intent
from fb.modules.base import Module, response

class HexModule(Module):

    uid="hex"
    name="Hex Functions"
    description="Functions for encoding/decoding hex strings"
    author="Michael Pratt (michael.pratt@bazaarvoice.com)"

    commands = {
        "decode": {
            "keywords": "hex2string",
            "function": "decodeUAS",
            "name": "Decode Hex",
            "description": "Decodes hexadecimal strings"
        }
    }

    def register(self):
        intent.service.registerCommand("decode", self.decodeHex, self, "Decode Auth String", "Decodes Auth Strings.")
        
    @response
    def decodeHex(self, bot, room, user, args):
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
               	
module = HexModule
