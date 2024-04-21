import tweepy


client = tweepy.Client("AAAAAAAAAAAAAAAAAAAAAKOjtQEAAAAAIGfUwwE6r4%2FHa3W3sfZPYnQ%2BbhI%3DgwEDSKF7yfffpfn8GXnAIJGGiyNoS8L2mh5RI5gH1tYsOiPlPv")

def get_tweets(query):
    tweets = client.search_all_tweets(query=query, expansions="referenced_tweets.id",).data

    if tweets is not None:
        res = []
        for tweet in tweets:
            root_tweet = (client.get_tweet(id=tweet.referenced_tweets[0].id, expansions="author_id"))
            author = client.get_user(id=root_tweet.data.author_id)
            res.append((author.data.username, root_tweet.data.text))
        return res

print(get_tweets("#test_EIRM is:reply"))

