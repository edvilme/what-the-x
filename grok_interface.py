import asyncio
import json
import re

from xai_sdk.ide import *

from dotenv import load_dotenv
load_dotenv()

COMPLETE_TWEET_PROMPT = """\
This is a conversation between a human user and a highly intelligent AI. The AI's name is Grok and it makes every effort to truthfully answer a user's questions. It always responds politely but is not shy to use its vast knowledge in order to solve even the most difficult problems. The conversation begins.

Human: I want you to help me complete the following tweets. I will provide you with a list of tweets and you must replace the most relevant word from each tweet with 3 underscores. 

You must then provide me with 4 options to choose from. These 4 options must contain the word you replaced and 3 other words.
The 3 other words must make sense within the context of the tweet, must keep the tweet grammatically correct, should not be part of the tweet and should be exactly one word.

You must then provide me with the correct answer as a list of one string.

Please format your answer as a valid JSON array. For eg. if the tweet is "AI is the future", and you chose to remove "AI" and replace it with 3 underscores, and the options are ["AI", "Machine", "Learning", "Intelligence"], and the answer is "AI", your output should be.
[{{
    id: 1,
    topic: "AI",
    original_tweet: "AI is the future", 
    modified_tweet: "___ is the future", 
    options: ["AI", "Machine", "Learning", "Intelligence"], 
    answer: ["AI"]
}}]<|separator|>

Assistant: Understood! Please provide the list of tweets.<|separator|>

Human: [
    {tweets}
]<|separator|>

Assistant:[{{
"""

class PromptInterface:
    def __init__(self, tweets):
        self.tweets = tweets

    @prompt_fn
    async def _generate_complete_tweet(self):
        _str = COMPLETE_TWEET_PROMPT.format(
            tweets=self.tweets, 
        )
        await prompt(_str)
        result = await sample(max_len=1024, stop_tokens=["<|separator|>"])
        print(as_string())

    async def generate_questions(self, question_type):
        TYPES_FUNCTIONS = {
            'complete': self._generate_complete_tweet,
        }

        func = TYPES_FUNCTIONS.get(question_type, lambda: f"Invalid question type: {question_type}")

        return await func()

    async def main(tweets):
        """Runs the example."""
        interface = PromptInterface(tweets)
        await interface.generate_questions('complete')

if __name__ == "__main__":
    json_file = 'data/tweets.json'
    with open(json_file) as json_data:
        tweet_objects = json.load(json_data)
    tweets = f"\t{',\n\t'.join(re.sub(r'#\S*', '', tweet['text']) for tweet in tweet_objects)}"

    asyncio.run(PromptInterface.main(tweets))
