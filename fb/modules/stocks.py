#Get Current Stock Price

import json, urllib

from fb.db import db

from twisted.python import log

import fb.intent as intent
from fb.modules.base import Module, require_auth, response

class StocksModule(Module):

	uid="stocks"
	name="Stocks"
	description="Functionality for stock quotes"
	author="Kyle Varga (kyle.varga@bazaarvoice.com)"

	commands = {
		"stock": {
			"keywords": "stock",
			"function": "stock",
			"name": "Stock Quote",
			"description": "Returns current Stock Price"
		}, 
		"stocktopic": {
			"keywords": "stocktopic",
			"function": "stocktopic",
			"name": "Stock Quote Topic",
			"description": "Returns currnet Stock Price to topic"
		}
	}

	@require_auth('stocks', "Stock search isn't allowed here!", False)
	@response
	def stock(self, bot, room, user, args):
		query = ','.join(args)
		url = "http://www.google.com/finance/info?infotype=infoquoteall&q=" + query
		print 'url= ' + url
		stock_response = urllib.urlopen(url)
		stock_results = stock_response.read()
		if len(stock_results) > 0:
			stock_results = stock_results[3:]
			stock_results = stock_results.replace('\\x26','&')
			results = json.loads(stock_results)
			msg = 'Stock Prices for ' + query + '\n'
			for data in results:
				closed = str(float(data["l"]) - float(data["c"]))
				msg += data['name'] + ' Yesterday Close: $' + closed + ' Today Open: $' + data['op'] + ' and is currently at  $' + data["l"] + ' (' + data["cp"] + '% from Close)\n'
		else:
			msg = 'No stocks found for ' + query
		return msg.strip()
		
	@require_auth('stocks', "Stock search isn't allowed here!", False)
	@response
	def stocktopic(self, bot, room, user, args):
		query = ','.join(args)
                url = "http://www.google.com/finance/info?infotype=infoquoteall&q=" + query
                print 'url= ' + url
                stock_response = urllib.urlopen(url)
                stock_results = stock_response.read()
                if len(stock_results) > 0:
                        stock_results = stock_results[3:]
                        results = json.loads(stock_results)
                        #msg = 'Stock Prices for ' + query + '\n'
                        for data in results:
                                msg = data['name'] + ' opened at $' + data['op'] + ' and is currently at  $' + data["l"] + ' (' + data["cp"] + '%)\n'
                else:
                        msg = 'No stocks found for ' + query

		room.setTopic(msg.strip())
		return False

module = StocksModule
