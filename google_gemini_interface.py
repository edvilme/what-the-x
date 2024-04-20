# https://colab.research.google.com/github/google/generative-ai-docs/blob/main/site/en/tutorials/python_quickstart.ipynb#scrollTo=G-zBkueElVEO
# !pip install -q -U google-generativeai

# Google API Key stored in .env file
# Generate key in: https://aistudio.google.com/app/apikey
from dotenv import load_dotenv
load_dotenv()

import json
import os

import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))

class JSONFormat:
    BASE_FORMAT = {
        "id": "1",
        "topic": "The topic of the tweet",
    }

    def _get_options_format(self):
        return {
            **self.BASE_FORMAT,
            "question": "What is the question?",
            "options": "The array of options for the question, containing the correct answer",
            "answer": "The correct option from the options as a list of one string"
        }

    def _get_complete_format(self):
        return {
            **self.BASE_FORMAT,
            "question": "The tweet with a blank space to complete",
            "options": "The array of options for the blank space, containing the correct answer",
            "answer": "The correct option from the options as a list of one string"
        }
    

class GeminiInterface:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.format = JSONFormat()

    def summarize_list_of_tweets(self, tweets):
        response = self.model.generate_content(f"""
            Give me a one sentence summary of the following tweets from different authors: \n \n
            {'\n'.join(tweets)}
        """)
        return response.text

    def generate_question_trivia(self, tweets):
        json_format = self.format._get_options_format()
        response = self.model.generate_content(f"""
            Create a one paragraph summary of each following tweets to generate trivia questions.
            You must use the following self-explaining JSON format: \n\n {json_format}.  \n\n
            {'\n'.join(tweets)}
        """)
        return response.text

    def generate_question_guess_author(self, tweets):
        json_format = self.format._get_options_format()
        response = self.model.generate_content(f"""
            Generate a question asking to guess the author of each following tweets.
            You must use the following self-explaining JSON format: \n\n {json_format}.  \n\n
            {'\n'.join(tweets)}
        """)
        return response.text

    def generate_question_complete_tweet(self, tweets):
        json_format = self.format._get_complete_format()
        response = self.model.generate_content(f"""
            For each of the following tweets, you must replace a word or a phrase with a blank space.
            
            You must use the following self-explaining JSON format: \n\n {json_format}.  \n\n
            {'\n'.join(tweets)}
        """)
        return response.text

    def generate_questions(self, question_type, tweets):
        TYPES_FUNCTIONS = {
            'trivia': self.generate_question_trivia,
            'guess': self.generate_question_guess_author,
            'complete': self.generate_question_complete_tweet,
        }

        question_func = TYPES_FUNCTIONS.get(question_type, lambda _: f"Invalid question type: {question_type}")

        return question_func(tweets)
    
    def generate_question(self, question):
        # TODO: remove me?
        response = self.model.generate_content(f"""
            Create a one paragraph summary of the following tweets from different authors to generate trivia questions.
            Use the json format: {{"topic": "trivia", "question": "What is the question?", "options": ["option1", "option2", "option3", "option4"], "answer": "option1}}
            Use the following tweets to generate the questions: \n \n
            {'\n'.join(question)}
        """)
        return response.text


if __name__ == "__main__":
    json_file = 'data/tweets.json'
    with open(json_file) as json_data:
        tweet_objects = json.load(json_data)
    tweets = [tweet['text'] for tweet in tweet_objects]

    interface = GeminiInterface()
    summary = interface.generate_questions('complete', tweets)
    print(summary)
