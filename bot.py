
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

hours = 12
if __name__ == "__main__":
    def check_price_difference():
        create_graph()
        diff = pricing["second"] - pricing["first"]
        percentage = str("{:2.2f}".format((diff/pricing["second"]) * 100 ))
        if diff >= 0:
            api.update_with_media("output_logo.png","The current #bitcoin price is : " + locale.currency(pricing["second"]) + " that is " + percentage + "%" + " higher in the last " + str(hours) + " hours")
        else:
            api.update_with_media("output_logo.png","The current #bitcoin price is : " + locale.currency(pricing["second"]) + " that is " +  percentage + "%" + " lower in the last " + str(hours) + " hours")

    def create_graph():
        dates = []
        prices = []

        data = get_coinbase_historical()

        for item in data:
            dates.insert(0, datetime.strptime(item["time"],'%Y-%m-%dT%H:%M:%SZ'))
            prices.insert(0, float(item["price"]))


        custom_style = Style(
            background='white',
            plot_background='white',
            opacity='.9',
            opacity_hover='.9',
            colors=('#EE494A','#EE494A')
        )

        offset = 0.2
        lowest  = min(prices) * (1 - offset)
        highest = max(prices) * (1 + offset)

        config = pygal.Config()
        config.style = custom_style
        config.title = "Bitcoin Price Last " + str(hours) + " Hours"
        config.y_title = "USD"
        config.y_label_rotation = 40
        config.x_label_rotation = 40
        config.show_dots = False
        config.style = custom_style
        config.range = lowest, highest
        config.margin = 20
        config.fill = True
        config.show_legend=False
        config.show_y_guides= False
        config.show_x_labels=False
        config.interpolate='cubic'

        line_chart = pygal.Line(config)
        line_chart.x_labels = map(lambda d: d.strftime('%m-%d %I:%M UTC'), dates)
        line_chart.add("", prices)
        line_chart.render_to_png(filename='output.png')

        mimage = Image.open('output.png')
        limage = Image.open('logo.png')
        limage = limage.resize((243, 49))
        mbox = mimage.getbbox()
        lbox = limage.getbbox()

        box = (mbox[2] - lbox[2] - lbox[2] - 38, mbox[1] - lbox[1] - lbox[1] + 30)
        mimage.paste(limage, box)
        mimage.save('output_logo.png')

    def get_coinbase():
        request = Request('https://api.coinbase.com/v2/prices/spot')
        response = urlopen(request)
        sub = json.loads(response.read())
        return float(sub["data"]["amount"])

    def get_coinbase_historical():
        request = Request('https://api.coinbase.com/v2/prices/historic?hours='+str(hours))
        response = urlopen(request)
        sub = json.loads(response.read())
        return sub["data"]["prices"]

    prices = get_coinbase_historical()
    pricing["first"] = float(prices[hours-1]["price"])
    pricing["second"] = float(get_coinbase())
    check_price_difference()
