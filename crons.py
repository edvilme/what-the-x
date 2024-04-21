import asyncio
import x_interface as x
import grok_interface as gi

from models import Quiz, User, Question, QuestionOption, Topic, db


from flask_apscheduler import APScheduler
scheduler = APScheduler()

RETRY_COUNT = 3

@scheduler.task('interval', id='generate_questions', seconds=60)
def generate_questions():
    tweets = x.get_tweets_in_reply_to("#trending")

    print("starting cron job")

    with db.atomic():
        quiz = Quiz.create(
            topic_id = Topic.get(Topic.id == 1),
            user_id = User.get(User.user_id == 1),
            name = 'trending'
        )

    for q_type in ('trivia', 'complete'):
        print(f"q_type={q_type}")
        count = 0
        results = None
        while count < RETRY_COUNT:
            asyncio.set_event_loop(asyncio.new_event_loop())
            results = asyncio.run(gi.GrokInterface(tweets).generate_questions(q_type))
            print(results)
            count += RETRY_COUNT if results else 1
        print("creating db records")
        results = results if isinstance(results, list) else [results]
        for result in results:
            with db.atomic():
                question = Question.create(
                    quiz_id = quiz.id,
                    type = q_type,
                    question = result['question'],
                    answer = result['answer']
                )
                for option in result['options']:
                    QuestionOption.create(
                        question_id = question.id,
                        option = option
                    )
    print("ending cron job")