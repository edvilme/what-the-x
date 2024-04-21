import asyncio
from datetime import datetime
from flask import Flask, render_template, request, session, redirect
from flask_session import Session

import os
import random
from urllib import parse
import tweepy

import x_interface as x
import grok_interface as g
from models import Quiz, User, QuestionOption
from crons import cron_generate_questions

from flask_apscheduler import APScheduler
scheduler = APScheduler()

# Config - Load environment variables

# Config - Load environment variables
from dotenv import load_dotenv
load_dotenv(".env")

# Config - Flask app
app = Flask(__name__, 
            static_url_path='', 
            static_folder='static')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Config - OAuth2
# Config - OAuth2
oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id = os.getenv('CLIENT_ID'),
    redirect_uri = os.getenv('REDIRECT_URI'),
    scope = ["tweet.read", "users.read", "list.read", "offline.access"],
    # Client Secret is only necessary if using a confidential client
    client_secret = os.getenv('CLIENT_SECRET'))

authorize_url = (oauth2_user_handler.get_authorization_url())
state = parse.parse_qs(parse.urlparse(authorize_url).query)['state'][0]

# Data - Questions
from models import *

QUESTIONS = []
# Data - Questions
from models import *

QUESTIONS = []

@app.route('/')
def hello():
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
    session["user_token"] = access_token

    return redirect("/me")

@app.route("/me")
def me():
    if not session.get("user_token"):
        return render_template('error.html', error_message="You are not authenticated")
    access_token = session.get("user_token")
    client = tweepy.Client(access_token)
    return session.get("user_token")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_message='uncaught exception'), 500

@app.route("/q/<string:username>/<string:quiz>")
def q(username, quiz):
    # Get quiz by name and username
    q = Quiz.select().join(User).where(User.username == username, Quiz.name == quiz)
    if not q:
        return render_template('error.html', error_message='Quiz not found'), 404
    # Get questions by quiz
    questions = Question.select().where(Question.quiz_id == q.get().id)
    if not questions:
        return render_template('error.html', error_message='Questions not found'), 404
    # Get random question
    question = random.choice(questions)
    # Add data to question
    question = {
        "id": question.id,
        "type": question.type,
        "question": question.question,
        "options": [option.option for option in question.options],
        "trending_topic": f"{q.get().topic_id.country}/{q.get().topic_id.name}",
    }
    return render_template('question.html', question=question)

@app.route("/question")
def question():
    return render_template("question.html", question=random.choice(QUESTIONS))

@app.route("/index")
def index():
    return render_template("index.html", question=random.choice(QUESTIONS))

@app.route("/tutorial")
def tutorial():
    return render_template("tutorial.html", question=random.choice(QUESTIONS))

@app.route("/answer/<int:question>", methods=["POST"])
def answer(question):
    answer = request.form.get("answer")
    if answer is None:
        return {"stauts": "error", "error": "Answer not found"}, 404
    # Get question by id
    q = Question.get(Question.id == question)
    if not q:
        return {"status": "error", "error": "Answer not found"}, 404
    # Check answer
    if q.answer == answer:
        return {"status": "correct"}
    return {"status": "incorrect"}
    
# Run cron_generate_questions as a background task only once
@scheduler.task('date', id='_cron_generate_questions', run_date=datetime.now())
def _cron_generate_questions():
    asyncio.run(cron_generate_questions())

scheduler.init_app(app)
scheduler.start()
app.run()