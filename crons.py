import asyncio
import re
import x_interface as x
import grok_interface as gi

from models import Quiz, User, Question, QuestionOption, Topic, db


RETRY_COUNT = 3

async def generate_questions():
    print("running cron job")
    # Get tweets
    tweets = x.get_tweets_in_reply_to("#WhatsTheX")
    if not tweets:
        return
    # Group tweets by username and text with list of tweets
    tweet_groups = {}
    for tweet in tweets:
        user_id = tweet["reply_author_id"] or 1
        username = tweet["reply_author_handle"] or "unknown"
        text = re.sub(r'[#@][^\s]+\ +', '', tweet["reply_tweet_text"])
        if (username, user_id, text) not in tweet_groups:
            tweet_groups[(username, user_id, text)] = []
        tweet_groups[(username, user_id, text)].append(tweet)
    print(tweet_groups)

    # Iterate over tweet groups
    for (username, user_id, text), tweets in tweet_groups.items():
        # Get or create user
        # TODO: Find user_id in database
        user = User.get_or_create(user_id=user_id, username=username, score=0)[0]
        # Get or create quiz
        quiz = Quiz.get_or_create(topic_id=1, user_id=user.user_id, name=text)[0]
        for type in ['complete', 'trivia']:
            # Questions
            questions = await gi.GrokInterface(tweets).generate_questions(type)
            # Assign questions to quiz
            for question in questions:
                q = Question.create(quiz_id=quiz.id, type=type, question=question['question'], answer=question['answer'])
                for option in question['options']:
                    QuestionOption.create(question_id=q.id, option=option)

            print(username, questions)

async def cron_generate_questions():
    while True:
        try:
            await generate_questions()
        except Exception as e:

            print("Error", e)
            pass
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(cron_generate_questions())