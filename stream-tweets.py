# Twitter Streaming Client 2016
# Description: Connect to Twitter's Streaming API and save received tweets.
# Disclaimer: Use only as directed by Twitter and at your own risk.
# Requirements:
# - Python3 (I use the Anaconda distro)
# - tweepy (https://www.tweepy.org/)
# - Twitter developer API keys, obtained from https://developer.twitter.com/en/docs


import csv
import tweepy


# Check if Place is in the United States
# Helper function: in_geography()
def in_geography(place):
    if place is not None: # If location passed in is empty, we're already done

        # then, if the place is a city within the US, we return true, else false.
        return place.country_code == 'US' and place.place_type == 'city' 
    else:
        return False

# Set the location geography you want to search within as you choose. Locations can be narrowed down
# further at a later point, but every geolocated Tweet within this bounding box will accrue towards
# your monthly cap
long_min = ...
lat_min = ...
long_max = ...
lat_max = ...
bbox = (long_min, lat_min, long_max, lat_max)

# Set path to output file (where the streamed Tweets appear) as you choose
output_file = ...

# Credentials to access Twitter data
consumer_key = ...
consumer_secret = ...
access_token = ...
access_token_secret = ...



"""
Here's what the above class is doing, explained in a concise way:
1. The class is listening for tweets that are posted with a location.
2. If the tweet is posted with a location, the class will check if the location is within a certain geography.
3. If the location is within the specified geography, the class will write the tweet's ID, text, place, bounding box, creation date, user ID, and user's friend count to a CSV file.
4. The class will also print the tweet's text and place to the console.
"""
class IDPrinter(tweepy.Stream):

    def on_status(self, status):
        if in_geography(status.place):
            writer = csv.writer(f)
            writer.writerow([status.id, status.text, status.place.full_name, status.place.bounding_box, 
                             status.created_at, status.user.id, status.user.friends_count])
            print(status.text, status.place.full_name)


# These are tokens that are necessary to stream Tweets. For more information go to developers.twitter.com
stream = IDPrinter(consumer_key, consumer_secret,
                   access_token,access_token_secret)


# Use on_status to write rows into the output (csv) file with the following header for Tweets in the
# bounding box defined 
with open(output_file, "w") as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Tweet', 'Place Name', 'Coordinates', 'Date-Time', 'UserID', 'UserFollowingCount'])
    stream.filter(locations=bbox)
