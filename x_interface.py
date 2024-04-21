import tweepy
import requests
import json
import geocoder

bearer_token = "AAAAAAAAAAAAAAAAAAAAAKOjtQEAAAAAIGfUwwE6r4%2FHa3W3sfZPYnQ%2BbhI%3DgwEDSKF7yfffpfn8GXnAIJGGiyNoS8L2mh5RI5gH1tYsOiPlPv"

client = tweepy.Client(bearer_token)

def get_data_woeid():
    file = open('data/woeid.json')
    data = json.load(file)
    return data

def get_woeid():
    city = geocoder.ip('me').city
    data = get_data_woeid()
    for dict in data:
        if dict['name'] == city:
            return dict['woeid']
    return 1

def get_tweets_in_reply_to(query):
    tweets = client.search_all_tweets(query=f"{query} is:reply", expansions=["referenced_tweets.id", "author_id"],).data

    if tweets is not None:
        res = []
        for tweet in tweets:
            root_tweet = (client.get_tweet(id=tweet.referenced_tweets[0].id, expansions="author_id"))
            print(root_tweet)
            author = client.get_user(id=root_tweet.data.author_id)
            res.append({
                "root_author_id": author.data.username, 
                "root_tweet_text": root_tweet.data.text,
                "reply_author_id": tweet.author_id,
                "reply_author_handle": client.get_user(id=tweet.author_id).data.username,
                "reply_tweet_text": tweet.text.replace(query, "")
            })
        return res
    return None

def get_trending_tweets():
    woeid = get_woeid()
    url = f"https://api.twitter.com/2/trends/by/woeid/{woeid}"
    headers = {'Authorization': f'Bearer {bearer_token}'}
    response = requests.get(url, headers=headers)
    data = response.json()['data']
    trends = {}
    for dict in data:
        trend = dict['trend_name']
        tweets = client.search_recent_tweets(trend).data
        trends[trend] = tweets
    return trends
