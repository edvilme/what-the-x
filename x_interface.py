import tweepy
import time
import atexit

client = tweepy.Client("AAAAAAAAAAAAAAAAAAAAAKOjtQEAAAAAIGfUwwE6r4%2FHa3W3sfZPYnQ%2BbhI%3DgwEDSKF7yfffpfn8GXnAIJGGiyNoS8L2mh5RI5gH1tYsOiPlPv")

def get_tweets_in_reply_to(query):
    tweets = client.search_all_tweets(query=f"{query} is:reply", expansions="referenced_tweets.id,author_id",).data

    if tweets is not None:
        res = []
        for tweet in filter(lambda tweet: tweet.referenced_tweets is not None, tweets):
            root_tweet = (client.get_tweet(id=tweet.referenced_tweets[0].id, expansions="author_id"))
            author = client.get_user(id=root_tweet.data.author_id)
            res.append({
                "root_author_id": author.data.username, 
                "root_tweet_text": root_tweet.data.text,
                "reply_author_id": tweet.author_id,
                "reply_author_handle": client.get_user(id=tweet.author_id).data.username,
                "reply_tweet_text": tweet.text.replace(query, "")
            })
        return res