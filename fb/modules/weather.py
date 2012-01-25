import fb.intent as intent
from fb.modules.base import FritbotModule, response

# requirements
import urllib#, simplejson

class WeatherModule(FritbotModule):

        name="Weather"
        description="Functions for returning weather"
        author="Kyle Varga (kyle.varga@bazaarvoice.com)"

	wundergroundapikey = '83f199a422e382c3'

        def register(self):
                intent.service.registerCommand("weather", self.getWeather, self, "Get Current Weather", "Gets the current weather.")
                
        @response
        def getWeather(self, bot, room, user, args):
		url = 'http://api.wunderground.com/api/' + self.wundergroundapikey + '/conditions/q/TX/Austin.json'
		#result = simplejson.load(urllib.urlopen(url))
		f = urllib.urlopen(url)
    		buff = f.read().replace('\\/', '/')
    		f.close()
    		result = eval(buff)
		current = result['current_observation']
		return 'Current Weather in Austin, TX: ' + current['weather'] + ', ' + current['temperature_string']
		#if 'Error' in result:
        		# An error occurred; raise an exception
        	#	return 'Error' +  result['Error']
    		#return result['ResultSet']

module = WeatherModule()
