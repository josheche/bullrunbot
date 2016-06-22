
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import sys
import random # Generates Random Numbers
import tweepy # Python Tweeting
import locale # Currency Library
import os
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
        diff = pricing["second"] - pricing["first"]
        if diff >= 0:
            api.update_status("The current #bitcoin price is : " + locale.currency(pricing["second"]) + " that is " + str("{:2.2f}".format((diff/pricing["second"]) * 100 ) + "%" + " higher since our last tweet")
        else:
            api.update_status("The current #bitcoin price is : " + locale.currency(pricing["second"]) + " that is " + str("{:2.2f}".format((diff/pricing["second"]) * 100 ) + "%" + " lower since our last tweet")

    def get_coinbase():
        request = Request('https://api.coinbase.com/v2/prices/spot')
        response = urlopen(request)
        sub = json.loads(response.read())
        return float(sub["data"]["amount"])

    while True:
        pricing["first"] = get_coinbase()
        time.sleep(60) #Tweet every 60 minutes (5 for testing) 
        pricing["second"] = get_coinbase()
        check_price_difference()
