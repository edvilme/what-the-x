from peewee import *
from dotenv import load_dotenv
import os
load_dotenv(".env")

# Config - Database
db = PostgresqlDatabase(os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'))

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = CharField(primary_key=True)
    username = CharField()
    score = IntegerField()

class Topic(BaseModel):
    country = CharField()
    name = CharField()

class Quiz(BaseModel):
    topic_id = ForeignKeyField(Topic, backref='quizzes')
    user_id = ForeignKeyField(User, backref='quizzes')
    name = CharField()

class Question(BaseModel):
    quiz_id = ForeignKeyField(Quiz, backref='questions')
    type = CharField()
    question = CharField()
    answer = CharField()

class QuestionOption(BaseModel):
    question_id = ForeignKeyField(Question, backref='options')
    option = CharField()

class QuestionAnswers(BaseModel):
    user_id = ForeignKeyField(User, backref='answers')
    question_id = ForeignKeyField(Question, backref='answers')
    correct = BooleanField()
    date = DateTimeField()

db.create_tables([User, Topic, Quiz, Question, QuestionOption, QuestionAnswers])