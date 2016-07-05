
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import sys
import random # Generates Random Numbers
import tweepy # Python Tweeting
import locale # Currency Library
import os
import pygal
from datetime import datetime
from urllib2 import Request, urlopen, URLError


#enter the corresponding information from your Twitter application into Heroku:
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_KEY = os.environ['ACCESS_KEY']
ACCESS_SECRET = os.environ['ACCESS_SECRET']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

pricing = {}
locale.setlocale( locale.LC_ALL, '' )


if __name__ == "__main__":
    def check_price_difference():
        create_graph()
        diff = pricing["second"] - pricing["first"]
        percentage = str("{:2.2f}".format((diff/pricing["second"]) * 100 ))
        if diff >= 0:
            api.update_with_media("output.svg","The current #bitcoin price is : " + locale.currency(pricing["second"]) + " that is " + percentage + "%" + " higher since our last tweet" + "\xF0\x9F\x93\x88")
        else:
            api.update_with_media("output.svg","The current #bitcoin price is : " + locale.currency(pricing["second"]) + " that is " +  percentage + "%" + " lower since our last tweet" + "\xF0\x9F\x93\x89")

    def create_graph():
        dates = []
        prices = []

        data = get_coinbase_historical()
        for item in data:
            dates.append(date.strptime(item["time"],'%Y-%B-%dT%H:%M:%SZ'))
            prices.append(float(item["price"]))


        line_chart = pygal.Line(x_label_rotation=15, fill=True)
        line_chart.x_labels = map(lambda d: d.strftime('%H:%M:%S'), dates)
        line_chart.add("Price", prices)
        line_chart.render_to_file('output.svg')

    def get_coinbase():
        request = Request('https://api.coinbase.com/v2/prices/spot')
        response = urlopen(request)
        sub = json.loads(response.read())
        return float(sub["data"]["amount"])

    def get_coinbase_historical():
        request = Request('https://api.coinbase.com/v2/prices/historic?hours=24')
        response = urlopen(request)
        sub = json.loads(response.read())
        return sub["data"]["prices"]

    while True:
        create_graph()
        pricing["first"] = get_coinbase()
        time.sleep(60*60*8) #Tweet every 60 minutes (5 for testing) 
        pricing["second"] = get_coinbase()
        check_price_difference()
