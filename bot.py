
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import sys
import random # Generates Random Numbers
import tweepy # Python Tweeting
import locale # Currency Library
import os, sys
import pygal
from PIL import Image
from pygal.style import Style
from datetime import datetime
from urllib2 import Request, urlopen, URLError


#enter the corresponding information from your Twitter application into Heroku:
try: 
    CONSUMER_KEY = os.environ['CONSUMER_KEY']
    CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
    ACCESS_KEY = os.environ['ACCESS_KEY']
    ACCESS_SECRET = os.environ['ACCESS_SECRET']
except KeyError:
    CONSUMER_KEY = ""
    CONSUMER_SECRET = ""
    ACCESS_KEY = ""
    ACCESS_SECRET = ""


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
            api.update_with_media("output_logo.png","The current #bitcoin price is : " + locale.currency(pricing["second"]) + " that is " + percentage + "%" + " higher since our last tweet" + "\xF0\x9F\x93\x88")
        else:
            api.update_with_media("output_logo.png","The current #bitcoin price is : " + locale.currency(pricing["second"]) + " that is " +  percentage + "%" + " lower since our last tweet" + "\xF0\x9F\x93\x89")

    def create_graph():
        dates = []
        prices = []

        average_price = 0
        price_amounts = 0

        data = get_coinbase_historical()

        for item in data:
            dates.insert(0, datetime.strptime(item["time"],'%Y-%m-%dT%H:%M:%SZ'))
            prices.insert(0, float(item["price"]))
            
            average_price += float(item["price"])
            price_amounts += 1


        average_price = average_price / price_amounts
        custom_style = Style(
            background='transparent',
            plot_background='transparent',
            opacity='.9',
            opacity_hover='.9',
            colors=('#EE494A','#EE494A')
        )

        config = pygal.Config()

        config.style = custom_style
        config.title = "Bitcoin Price (Last 8 Hours)"
        config.y_title = "USD"
        config.y_label_rotation = 40
        config.x_label_rotation = 40
        config.show_dots = False
        config.style = custom_style
        config.range = (average_price - (average_price/50), average_price + (average_price/50))
        config.margin = 20
        config.fill = True
        config.show_legend=False
        config.show_y_guides= False
        config.show_x_labels=False
        config.interpolate='cubic'

        #line_chart = pygal.Line(show_dots=False, style=custom_style, range=(average_price - (average_price/50), average_price + (average_price/50)),title="Bitcoin Price (Last 8 Hours)", x_title="Time", y_title="USD", margin=20, y_label_rotation=40, x_label_rotation=40, fill=True, show_legend=False, show_y_guides= False, interpolate='cubic')
        line_chart = pygal.Line(config)
        line_chart.x_labels = map(lambda d: d.strftime('%m-%d %I:%M UTC'), dates)
        line_chart.add("", prices)
        line_chart.render_to_png(filename='output.png')

        mimage = Image.open('output.png')
        limage = Image.open('logo.png')
        limage = limage.resize((243, 49))
        mbox = mimage.getbbox()
        lbox = limage.getbbox()

        box = (mbox[2] - lbox[2] - lbox[2] - 20, mbox[1] - lbox[1] - lbox[1] + 30)
        mimage.paste(limage, box)
        mimage.save('output_logo.png')
        print 'Rendered'

    def get_coinbase():
        request = Request('https://api.coinbase.com/v2/prices/spot')
        response = urlopen(request)
        sub = json.loads(response.read())
        return float(sub["data"]["amount"])

    def get_coinbase_historical():
        request = Request('https://api.coinbase.com/v2/prices/historic?hours=8')
        response = urlopen(request)
        sub = json.loads(response.read())
        return sub["data"]["prices"]

    while True:
        create_graph()
        pricing["first"] = get_coinbase()
        time.sleep(60*60*8) #Tweet every 60 minutes (5 for testing) 
        pricing["second"] = get_coinbase()
        check_price_difference()
