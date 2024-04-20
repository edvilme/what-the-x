from flask import Flask, render_template, request
import random

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

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

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