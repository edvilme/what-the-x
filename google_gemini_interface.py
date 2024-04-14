# https://colab.research.google.com/github/google/generative-ai-docs/blob/main/site/en/tutorials/python_quickstart.ipynb#scrollTo=G-zBkueElVEO
# !pip install -q -U google-generativeai

# Google API Key stored in .env file
# Generate key in: https://aistudio.google.com/app/apikey
from dotenv import load_dotenv
load_dotenv()

import os

import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))

def summarize_list_of_tweets(tweets):
    model = genai.GenerativeModel('gemini-pro')
    # See this for prompt generation: https://ai.google.dev/docs/concepts#generate-list
    response = model.generate_content(f"""
        Give me a one sentence summary of the following tweets from different authors: \n \n
        {'\n'.join(tweets)}
    """)
    return response.text

tweet_objects = [
    {
        "id": 1,
        "text": "I love my dog",
        "user": "user1",
        "created_at": "2022-01-01"
    },
    {
        "id": 2,
        "text": "I love my cat",
        "user": "user2",
        "created_at": "2022-01-02"
    },
    {
        "id": 3,
        "text": "I love my fish",
        "user": "user3",
        "created_at": "2022-01-03"
    },
]
 
summary = summarize_list_of_tweets([tweet['text'] for tweet in tweet_objects])
print(summary)
