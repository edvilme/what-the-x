from flask import Flask, render_template, request, url_for

import os
import random
import oauth2 as oauth
import urllib.request
from urllib import parse
import urllib.error
import json
import tweepy

app = Flask(__name__, 
            static_url_path='', 
            static_folder='static')

QUESTIONS = [
    {
        'id': 1,
        'type': 'trivia',
        'trending_topic': 'testing', 
        'question': "What is the answer to life, the universe, and everything?",
        'options': ['42', '24', '0', '1'],
        'answer': '42'
    },
    {
        'id': 2,
        'type': 'trivia',
        'trending_topic': 'testing',
        'question': "What is the capital of France?",
        'options': ['Paris', 'London', 'Berlin', 'Madrid'],
        'answer': 'Paris'
    }, 
    {
        'id': 3,
        'type': 'trivia',
        'trending_topic': 'testing',
        'question': "What is the largest mammal in the world?",
        'options': ['Blue Whale', 'Elephant', 'Giraffe', 'Hippopotamus'],
        'answer': 'Blue Whale'
    }
]

app.debug = False

oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id = os.getenv('CLIENT_ID'),
    redirect_uri = os.getenv('REDIRECT_URI'),
    scope = ["tweet.read", "users.read", "list.read"],
    # Client Secret is only necessary if using a confidential client
    client_secret = os.getenv('CLIENT_SECRET'))

authorize_url = (oauth2_user_handler.get_authorization_url())

state = parse.parse_qs(parse.urlparse(authorize_url).query)['state'][0]

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/start')
def start():
    return render_template('start.html', authorize_url=authorize_url)


@app.route('/callback')
def callback():
    # Accept the callback params, get the token and call the API to
    # display the logged-in user's name and handle
    received_state = request.args.get('state')
    code = request.args.get('code')
    access_denied = request.args.get('error')

    # if the OAuth request was denied, delete our local token
    # and show an error message
    if access_denied:
        return render_template('error.html', error_message="the OAuth request was denied by this user")
      
    if received_state != state:
      return render_template('error.html', error_message="There was a problem authenticating this user")
    
    redirect_uri = os.getenv('REDIRECT_URI')
    response_url_from_app = '{}?state={}&code={}'.format(redirect_uri, state, code)
    access_token = oauth2_user_handler.fetch_token(response_url_from_app)['access_token']
    print(access_token)
    client = tweepy.Client(access_token)
    user = client.get_me(user_auth=False, user_fields=['public_metrics'], tweet_fields=['author_id'])
    print(user)

    name = user.data['name']
    user_name = user.data['username']
    followers_count = user.data['public_metrics']['followers_count']
    friends_count = user.data['public_metrics']['following_count']
    tweet_count = user.data['public_metrics']['tweet_count']
    
    return render_template('callback-success.html', name=name, user_name=user_name,
                           friends_count=friends_count, tweet_count=tweet_count, followers_count=followers_count)


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_message='uncaught exception'), 500

@app.route("/question")
def question():
    return render_template("question.html", question=random.choice(QUESTIONS))

@app.route("/answer/<int:question>", methods=["POST"])
def answer(question):
    # Search question by id
    q = next((q for q in QUESTIONS if q['id'] == question), None)
    if not q:
        return {'status': 'error'}, 404
    if q['answer'] == request.form['answer']:
        return {'status': 'correct_answer'}
    else:
        return {'status': 'wrong_answer', 'correct_answer': q['answer']}
    
if __name__ == '__main__':
    app.run()