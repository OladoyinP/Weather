from twython import TwythonStreamer
import pyodbc
import json
import datetime
import time
import pymongo
from pymongo import MongoClient

client = MongoClient()
db = client.test_tweets

# Define a list, each element will be all information on a given tweet
tweets = []

# No. of days for which we want the code to run
days = 1

class MyStreamer(TwythonStreamer):
    def on_success(self, data):

        NOW = datetime.datetime.now().time().hour

        # As long as it is in english, append the entire status to the list
        if data['lang'] == 'en':
            tweets.append(data)
            print 'tweet #' + str(len(tweets))

        # Limit of grabbing tweets is 2400, best to be safe?
        if len(tweets) >= 2:
            print 'done'
            self.disconnect()

        # If we grab a tweet after 11 PM STOP
        if NOW >= 23:
            self.disconnect()

    def on_error(self, status_code, data):
        print status_code, data
        self.disconnect()

# Start grabbing tweets
def tweetsperday():
    stream = MyStreamer('Twitter API key', 'twitter Secret Key',
                        'Access Token',
                        'Access Token Secret')
    # In the track filer, comma separation = OR, space separation = AND
    # Cannot filer by location also..
    stream.statuses.filter(track=[' YOUR SEARCH TERMS '])#'London weather,soho weather,greenwich weather,twickenham weather,wembley weather,waterloo weather,whitechapel weather,buckingham palace weather,hyde park weather,Barking and Dagenham weather,Barnet weather,Bexley weather,Brent weather,Bromley weather'])

# Send the tweets to MONGO
def Commit(tweets):
    for t in tweets:
        db.tweets.insert_one(t)

# Loop through the tweet grabbing, once a day
for i in range(days):
    CurrentDay = datetime.datetime.now().day
    # Grab tweets
    tweetsperday()

    Commit(tweets)

    tweets = []
    # Empty Tweets for using again
    CurrentHour = datetime.datetime.now().time().hour
    # If we are before twelve oclock, wait until it is 12 oclock
    if CurrentHour < 12:
        time.sleep((12 - CurrentHour) * 60 * 60)

    # Now it is after midday, grab another 750 tweets
    tweetsperday()

    # Send the tweets to SQL
    Commit(tweets)

    # Empty tweets for using again
    tweets = []
    CurrentHour = datetime.datetime.now().time().hour
    # If we are before five oclock, wait until it is five oclock
    if CurrentHour < 17:
        time.sleep((17 - CurrentHour) * 60 * 60)
    # Now it is after five, grab another 750 tweets
    tweetsperday()
    Commit(tweets)

    # Now lets do it every day
    # Is it before 6 am? wait until 6 am..
    CurrentHour = datetime.datetime.now().time().hour
    #if CurrentHour < 6:
     #   time.sleep((6 - CurrentHour) * 60 * 60)
        # Restart the function
    # Is it after 7 and before midnight? Wait till midnight, then wait till 7 am
    DayNow = datetime.datetime.now().day
    if DayNow == CurrentDay:
        if CurrentHour <= 23:
            time.sleep((24 - CurrentHour) * 60 * 60)
            #Restart the function
