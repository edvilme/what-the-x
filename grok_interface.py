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

                Please format your answer as a valid JSON array. For example, if the question you generated is "What word is the most used?", and the options are ["The most used word is 'car'", "The most use word is 'winter'", "The most used word is 'universe'", "There is no most used words"], and the answer is "The most use word is 'winter'", your output should be.
                [{{
                    id: 1,
                    topic: "AI",
                    question: "What word is the most used?", 
                    options: ["The most used word is 'car'", "The most use word is 'winter'", "The most used word is 'universe'", "There is no most used words"], 
                    answer: "The most use word is 'winter'"
                }}]<|separator|>

                Assistant: Understood! Please provide the list of tweets.<|separator|>

                Human: [
                    {tweets}
                ]<|separator|>

                Assistant:
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
                    id: 1,
                    topic: "AI",
                    original_tweet: "AI is the future", 
                    modified_tweet: "___ is the future", 
                    options: ["AI", "Machine", "Learning", "Intelligence"], 
                    answer: "AI"
                }}]<|separator|>

                Assistant: Understood! Please provide the list of tweets.<|separator|>

                Human: [
                    {tweets}
                ]<|separator|>

                Assistant:
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
            result = json.loads(result.as_string())
        except json.JSONDecodeError:
            print("Error: Could not decode JSON response.")
            return
        
        return result

if __name__ == "__main__":
    json_file = 'data/tweets.json'
    with open(json_file) as json_data:
        tweet_objects = json.load(json_data)
    tweets = f"\t{',\n\t'.join(re.sub(r'#\S*', '', tweet['text']) for tweet in tweet_objects)}"
    
    interface = GrokInterface(tweets)
    r = asyncio.run(interface.generate_questions('trivia'))
    print(r)
