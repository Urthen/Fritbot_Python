#Get Current Stock Price

import json, urllib
from fb.db import db

from twisted.python import log

import fb.intent as intent
from fb.modules.base import FritbotModule, response

class StocksModule(FritbotModule):

	name="Stocks"
	description="Functionality for stock quotes"
	author="Kyle Varga (kyle.varga@bazaarvoice.com)"

	def register(self):
		intent.service.registerCommand("stock", self.stock, self, "Stock Quote", "Returns current Stock Price")

	@response
	def stock(self, bot, room, user, args):
		query = ','.join(args)
		print 'query = ' + query
		url = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where%20symbol%20%3D%20%22" +query + "%22&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback="
		url = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where%20symbol%20%3D%20'" + query + "'&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback="
		url = "http://query.yahooapis.com/v1/public/yql?q="
		url += "select * from yahoo.finance.quotes where symbol = '" + query + "'"
		url = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where%20symbol%20%3D%20'BV'&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback="
		url = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where%20symbol%20in%20(%22BV%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback="
		url = "http://www.google.com/finance/info?infotype=infoquoteall&q=" + query
		print 'url= ' + url
		stock_response = urllib.urlopen(url)
		stock_results = stock_response.read()
		if len(stock_results) > 0:
			print 'read:' + stock_results
			stock_results = stock_results[3:]
			print 'withoutfirst3:' + stock_results
			results = json.loads(stock_results)
			print results
			msg = 'Stock Prices for ' + query + '\n'
			for data in results:
				msg += data['name'] + ' opened at $' + data['op'] + ' and is currently at  $' + data["l"] + '\n'
		else:
			msg = 'No stocks found for ' + query
		
		return msg

module = StocksModule()


