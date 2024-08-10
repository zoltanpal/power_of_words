import hashlib
import time
from operator import and_

import feedparser
from dateutil import parser
from nltk import word_tokenize
from nltk.corpus import stopwords

from app.models.feeds import Feeds
from app.models.sources import Sources
from config import pow_db_config_str
from libs.database import initialize_database, session_scope
from libs.functions import setup_logging_to_file, remove_photo_video, clean_url
from libs.sentiment_analyzer import get_sentiment_prediction, get_emotion_prediction

initialize_database(pow_db_config_str)
stopwords = stopwords.words("hungarian")

error_logger = setup_logging_to_file('error.log')
info_logger = setup_logging_to_file('info.log')

# Get the sources
with session_scope() as session:
    rss_sources = session.query(Sources.id, Sources.rss).all()


def not_in_db(hash: str, source_id: int) -> bool:
    with session_scope() as session:
        cursor_result = (
            session.query(Feeds)
            .filter(and_(Feeds.hash == hash, Feeds.source_id == source_id))
            .first()
        )
    return cursor_result == 0 or cursor_result is None


def run_job():
    st = time.time()
    count = 0
    for rss_source in rss_sources:
        rss_source_id = rss_source[0]
        rss_source_link = rss_source[1]
        rss_feed = feedparser.parse(rss_source_link)
        if 'status' not in rss_feed:
            error_logger.error(f'Error in reading RSS: {rss_source_link}')
            continue
        if rss_feed["status"] != 200:
            error_logger.error(f'Error in reading RSS: {rss_source_link}, status: {rss_feed["status"]}')
            continue

        for item in rss_feed["entries"]:
            title = remove_photo_video(item["title"]).strip()
            link = clean_url(item["link"]).strip()
            hash = hashlib.md5(bytes(link, encoding='utf-8')).hexdigest()

            if not_in_db(hash=hash, source_id=rss_source_id):
                words = [word.lower() for word in word_tokenize(title) if
                         word.lower() not in stopwords and len(word) > 2]

                datetime_object = parser.parse(item["published"])
                feed_date = datetime_object.strftime("%Y-%m-%d")
                sentiment_prediction_dict = get_sentiment_prediction(title)
                emotion_prediction_dict = get_emotion_prediction(title)

                new_feed = Feeds(
                    title=title,
                    link=link,
                    source_id=rss_source_id,
                    words=words,
                    published=parser.parse(item["published"]),
                    feed_date=feed_date,
                    hash=hash,
                    sentiment_prediction=sentiment_prediction_dict,
                    negative=sentiment_prediction_dict['negative'],
                    positive=sentiment_prediction_dict['positive'],
                    neutral=sentiment_prediction_dict['neutral'],
                    emotion_prediction=emotion_prediction_dict,
                    anger=emotion_prediction_dict['anger'],
                    fear=emotion_prediction_dict['fear'],
                    joy=emotion_prediction_dict['joy'],
                    sadness=emotion_prediction_dict['sadness'],
                    love=emotion_prediction_dict['love'],
                    surprise=emotion_prediction_dict['surprise']
                )
                with session_scope() as session:
                    session.add(new_feed)
                    session.commit()

    et = time.time()
    info_logger.info(f"script run: {et - st}")


run_job()
