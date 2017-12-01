import json
import os
import random
import re
import requests
import string
import tweepy
import urllib

consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

labels = {
    'hardcore': [
        {
            'name':'Deathwish Inc',
            'id': 74737
         },
        {
            'name': 'Dischord',
            'id': 18955
        },
        {
            'name': 'Triple-B',
            'id': 162232
        },
        {
            'name': 'Nemesis',
            'id': 252938
        },
    ],
    'punk' : [
        {
            'name': 'Epitaph',
            'id': 61599
        },
        {
            'name': 'Sub Pop',
            'id': 77343
        },
        {
            'name': 'Equal Vision',
            'id': 33333
        },
        {
            'name': 'Touch & Go',
            'id': 819
        },
        {
            'name': 'Jade Tree',
            'id': 18608
        },
        {
            'name': 'Doghouse',
            'id': 42349
        },
    ],
    'indie' : [
        {
            'name': 'Epitaph',
            'id': 61599
        },
        {
            'name': '6131',
            'id': 134927
        },
        {
            'name': 'No Sleep Records',
            'id': 156292
        },
    ]
}


def tweet_pressing_info(event, context):
    headers = {
        'User-Agent': 'Vinyl Pressing Bot 1.0'
    }

    # grab a random record label
    label_choice = random.choice(labels.get(random.choice(list(labels.keys()))))
    label_id = label_choice['id']
    label_name = label_choice['name']

    label_uri = 'https://api.discogs.com/labels/{}/releases?page=10&per_page=1'.format(label_id)
    site = requests.get(label_uri, headers)
    if site.status_code == 200:
        # get total number of releases
        label_data = json.loads(site.text)
        total = label_data['pagination']['pages']

        # get a random album
        rand_record = random.randint(1,total)
        album_uri = 'https://api.discogs.com/labels/{}/releases?page={}&per_page=1'.format(label_id,
                                                                                            rand_record)
        album_response = requests.get(album_uri, headers)
        if album_response.status_code == 200:
            album_info = json.loads(album_response.text)
            album_id = album_info['releases'][0]['id']

            #get notes on album
            full_album_uri = 'https://api.discogs.com/releases/{}'.format(album_id)
            full_album_response = requests.get(full_album_uri, headers)
            if full_album_response.status_code == 200:
                full_album_details = json.loads(full_album_response.text)

                pressing_info = full_album_details['notes'].strip() \
                    if 'notes' in full_album_details else 'No information available'
                band_and_album = full_album_details['artists'][0]['name'] + ' - ' \
                                 + full_album_details['title']
                pressing_info = band_and_album + ' - ' + label_name + '\n' + pressing_info
                pressing_info = pressing_info.replace("First Pressing", "1st Press")
                pressing_info = pressing_info.replace("Second Pressing", "2nd Press")
                pressing_info = pressing_info.replace("Test Pressing", "Test Press")
                vinyls = (pressing_info[:138] + '..') if len(pressing_info) > 138 else pressing_info

                parsed_band_and_album = urllib.parse.quote(band_and_album)
                link = 'https://www.amazon.com/s/ref=as_li_ss_tl?url=search-alias=popular&field-keywords=' \
                       '{}&rh=n:5174,k:{}&linkCode=sl2&tag=hosyoed-20'.format(parsed_band_and_album,parsed_band_and_album)
                # throw in that url
                vinyls += ' ' + link
                print(vinyls)
                auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
                auth.set_access_token(access_token, access_token_secret)
                api = tweepy.API(auth)
                api.update_status(vinyls)

if __name__ == "__main__":
    tweet_pressing_info(None, None)