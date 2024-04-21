from peewee import *
from dotenv import load_dotenv
import os
load_dotenv(".env")

# Config - Database
db = PostgresqlDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = CharField(primary_key=True)
    username = CharField()
    score = IntegerField()

class Topic(BaseModel):
    id = CharField(primary_key=True)
    country = CharField()
    name = CharField()

class Quiz(BaseModel):
    id = CharField(primary_key=True)
    topic_id = ForeignKeyField(Topic, backref='quizzes')
    user_id = ForeignKeyField(User, backref='quizzes')
    name = CharField()

class Question(BaseModel):
    id = CharField(primary_key=True)
    quiz_id = ForeignKeyField(Quiz, backref='questions')
    type = CharField()
    question = CharField()
    answer = CharField()

class QuestionOption(BaseModel):
    id = CharField(primary_key=True)
    question_id = ForeignKeyField(Question, backref='options')
    option = CharField()

db.init(os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'))
db.create_tables([User, Topic, Quiz, Question, QuestionOption])