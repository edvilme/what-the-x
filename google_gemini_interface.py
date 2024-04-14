# https://colab.research.google.com/github/google/generative-ai-docs/blob/main/site/en/tutorials/python_quickstart.ipynb#scrollTo=G-zBkueElVEO
# !pip install -q -U google-generativeai

# Google API Key stored in .env file
# Generate key in: https://aistudio.google.com/app/apikey
from dotenv import load_dotenv
load_dotenv()

import os

import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))

model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("What is the meaning of life?")
print(response.text)