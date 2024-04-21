from datetime import datetime
from flask import Flask, render_template, request, session, redirect
from flask_session import Session

import os
import random
from urllib import parse
import tweepy

from models import Quiz, User, Question, QuestionAnswers


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
oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id = os.getenv('CLIENT_ID'),
    redirect_uri = os.getenv('REDIRECT_URI'),
    scope = ["tweet.read", "users.read", "list.read", "offline.access"],
    # Client Secret is only necessary if using a confidential client
    client_secret = os.getenv('CLIENT_SECRET'))

authorize_url = (oauth2_user_handler.get_authorization_url())
state = parse.parse_qs(parse.urlparse(authorize_url).query)['state'][0]


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

    # Create user if not exists
    user = tweepy.Client(access_token).get_me().data
    User.get_or_create(user_id=user["id"], username=user["screen_name"], score=0)

    return redirect("/index")

@app.route("/me")
def me():
    if not session.get("user_token"):
        return render_template('error.html', error_message="You are not authenticated")
    return session.get("user_token")

@app.route("/q/<string:username>/<string:q>")
def q(username, q):
    # Require login
    if not session.get("user_token"):
        return render_template('error.html', error_message="You are not authenticated")

    twitter_user = tweepy.Client(session.get("user_token")).get_me(user_auth=False).data

    quiz = Quiz.select().join(User).where(User.username == username, Quiz.name == q)
    if not quiz:
        return render_template('error.html', error_message='Quiz not found'), 404

    questions = Question.select()\
        .where(Question.quiz_id == quiz.get().id, Question.id.not_in(QuestionAnswers.select(QuestionAnswers.question_id)\
        .where(QuestionAnswers.user_id == twitter_user.id)))    
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

@app.route("/answer/<int:question>", methods=["POST"])
def answer(question):
    if not session.get("user_token"):
        return {"status": "error", "error": "User not authenticated"}, 401
    content = request.get_json(silent=True)
    answer = content.get("answer")
    if answer is None:
        return {"stauts": "error", "error": "Answer not found"}, 404
    # Get question by id
    q = Question.get(Question.id == question)
    if not q:
        return {"status": "error", "error": "Question not found"}, 404
    # Get user data
    user = tweepy.Client(session.get("user_token")).get_me().data
    user_id = user.get("id")
    
    # Save answer
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        return {"status": "error", "error": "User not found"}, 404
    # Save answer
    QuestionAnswers.create(
        user_id=User.get(User.user_id == user["id"]),
        question_id=question,
        correct=q.answer == answer,
        date=datetime.now()
    )
    # Check answer
    if q.answer == answer:
        user.score += 100
        user.save()
        return {"status": "correct", "score": user.score}
    return {"status": "incorrect"}

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")    

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_message='uncaught exception'), 500
