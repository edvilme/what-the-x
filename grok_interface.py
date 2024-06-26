import asyncio
import json
import re

from xai_sdk.ide import *

from dotenv import load_dotenv
load_dotenv()

PREAMBLE = "This is a conversation between a human user and a highly intelligent AI. The AI's name is Grok and it makes every effort to truthfully answer a user's questions. It always responds politely but is not shy to use its vast knowledge in order to solve even the most difficult problems. The conversation begins."

class GrokInterface:
    def __init__(self, tweets, max_len=1024):
        self.tweets = tweets
        self.max_len = max_len

    def _get_trivia_tweet_prompt(self):
        return """
                {preamble}

                Human: I want you to read the list of tweets I will provide you and generate a summary question about them and its answer. 

                You must then provide me 4 options to choose from. These 4 options must contain the answer to the question.

                You must then provide me with the correct answer as a string.

                Please format your answer as a valid JSON array. 
                Provide human understandable questions, I want to ask about the tweet to someone who read, and the question is to see if they remembered or understood
                [{{
                    topic: "replace this text with the topic the question belong to",
                    question: "Replace this text with the question formulated", 
                    options: ["replace this text with option answer 1", "replace this text with option answer 2", "replace this text with option answer 3", "replace this text with option answer 4"], 
                    answer: "replace this text with the answer"
                }}]<|separator|>

                Assistant: Understood! Please provide the list of tweets and I will output an array of valid JSON.<|separator|>

                Human: [
                    {tweets}
                ]<|separator|>

                Assistant: [{{
        """.format(preamble=PREAMBLE, tweets=self.tweets)

    def _get_complete_tweet_prompt(self):
        return """
                {preamble}

                Human: I want you to help me complete the following tweets. I will provide you with a list of tweets and you must replace the most relevant word from each tweet with 3 underscores. 

                You must then provide me 4 options to choose from. These 4 options must contain the word you replaced and 3 other words.
                The 3 other words must make sense within the context of the tweet, must keep the tweet grammatically correct, should not be part of the tweet and should be exactly one word.

                You must then provide me with the correct answer as a string.

                Please format your answer as a valid JSON array. For eg. if the tweet is "AI is the future", and you chose to remove "AI" and replace it with 3 underscores, and the options are ["AI", "Machine", "Learning", "Intelligence"], and the answer is "AI", your output should be.
                [{{
                    topic: "replace this text with the topic the prompt belong to",
                    question: "Replace this text with the tweet and a _ simulating blank space", 
                    options: ["replace this text with option answer 1", "replace this text with option answer 2", "replace this text with option answer 43, "replace this text with option answer 4"], 
                    answer: "replace this text with the answer"
                }}]<|separator|>

                Assistant: Understood! Please provide the list of tweets.<|separator|>

                Human: [
                    {tweets}
                ]<|separator|>

                Assistant: [{{
        """.format(preamble=PREAMBLE, tweets=self.tweets)

    async def generate_questions(self, question_type):
        PROMPTS_FUNCTIONS = {
            'trivia': self._get_trivia_tweet_prompt,
            'complete': self._get_complete_tweet_prompt,
        }

        if question_type not in PROMPTS_FUNCTIONS:
            raise ValueError(f"Invalid question type: {question_type}")

        prompt_text = PROMPTS_FUNCTIONS[question_type]()

        await prompt(prompt_text)
        result = await sample(max_len=self.max_len, stop_tokens=["<|separator|>"])
        
        try:
            # Grok does not format the JSON list correctly anymore...
            result = json.loads(f'[{{{result.as_string()}')
        except json.JSONDecodeError:
            print("Error: Could not decode JSON response.")
            return
        
        return result
