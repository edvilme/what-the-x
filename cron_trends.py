import asyncio
import re
import x_interface as x
import grok_interface as gi

from models import Quiz, User, Question, QuestionOption, Topic, db


RETRY_COUNT = 3

async def generate_questions_by_trend():
    print("running trend cron job")
    # Get tweets
    tweets = x.get_trending_tweets()

    for trend, texts in tweets.items():
        # Get or create user
        user_data = x.get_user_data('edvilme')
        user = User.get_or_create(user_id=user_data[0], username=user_data[1], score=0)[0]

        # Get or create quiz
        quiz = Quiz.get_or_create(topic_id=1, user_id=user.user_id, name="daily_trend")[0]
        for type in ['complete', 'trivia']:
            # Questions
            questions = await gi.GrokInterface(texts).generate_questions(type)
            # Assign questions to quiz
            for question in questions:
                q = Question.create(quiz_id=quiz.id, type=type, question=question['question'], answer=question['answer'])
                for option in question['options']:
                    QuestionOption.create(question_id=q.id, option=option)
                print(trend, questions)

async def cron_generate_questions_by_trend():
    while True:
        try:
            await generate_questions_by_trend()
        except Exception as e:
            print("Error", e)
            pass
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(cron_generate_questions_by_trend())
