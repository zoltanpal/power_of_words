import hashlib
import time
from operator import and_

import feedparser
from dateutil import parser as dateparser
from nltk import word_tokenize
from nltk.corpus import stopwords

from app.models.feeds import Feeds
from app.models.sources import Sources
from config import pow_db_config_str
from libs.database import initialize_database, session_scope
from libs.functions import clean_url, remove_photo_video, setup_logging_to_file
from libs.sentiment_analyzer import get_emotion_prediction, get_sentiment_prediction

# Initialize the database
initialize_database(pow_db_config_str)

# Load Hungarian stopwords
stopwords_list = stopwords.words("hungarian")

# Set up logging
error_logger = setup_logging_to_file("error.log")
info_logger = setup_logging_to_file("info.log")

# Fetch RSS sources from the database
with session_scope() as session:
    rss_sources = session.query(Sources.id, Sources.rss).all()


def not_in_db(hash: str, source_id: int) -> bool:
    """
    Checks if a feed with a given hash and source_id already exists in the database.

    Args:
        hash (str): The MD5 hash of the feed link.
        source_id (int): The ID of the RSS source.

    Returns:
        bool: True if the feed does not exist, False otherwise.
    """
    with session_scope() as session:
        cursor_result = (
            session.query(Feeds)
            .filter(and_(Feeds.hash == hash, Feeds.source_id == source_id))
            .first()
        )
    return cursor_result == 0 or cursor_result is None


def process_feed_item(item, rss_source_id: int) -> None:
    """
    Processes a single RSS feed item, analyzing its sentiment, emotions,
    and saving it to the database if it doesn't already exist.

    Args:
        item: The RSS feed item.
        rss_source_id (int): The ID of the RSS source.
    """
    title = remove_photo_video(item["title"]).strip()
    link = clean_url(item["link"]).strip()
    hash = hashlib.md5(link.encode("utf-8")).hexdigest()

    if not_in_db(hash=hash, source_id=rss_source_id):
        words = [
            word.lower()
            for word in word_tokenize(title)
            if word.lower() not in stopwords_list and len(word) > 2
        ]

        published_date = dateparser.parse(item["published"])
        feed_date = published_date.strftime("%Y-%m-%d")

        # Sentiment and emotion predictions
        sentiment_prediction_dict = get_sentiment_prediction(title)
        emotion_prediction_dict = get_emotion_prediction(title)

        # Create a new feed entry
        new_feed = Feeds(
            title=title,
            link=link,
            source_id=rss_source_id,
            words=words,
            published=published_date,
            feed_date=feed_date,
            hash=hash,
            sentiment_prediction=sentiment_prediction_dict,
            negative=sentiment_prediction_dict["negative"],
            positive=sentiment_prediction_dict["positive"],
            neutral=sentiment_prediction_dict["neutral"],
            emotion_prediction=emotion_prediction_dict,
            anger=emotion_prediction_dict["anger"],
            fear=emotion_prediction_dict["fear"],
            joy=emotion_prediction_dict["joy"],
            sadness=emotion_prediction_dict["sadness"],
            love=emotion_prediction_dict["love"],
            surprise=emotion_prediction_dict["surprise"],
        )

        # Save the new feed to the database
        with session_scope() as session:
            session.add(new_feed)
            session.commit()


def run_job():
    """
    Runs the RSS feed processing job. Fetches RSS feeds from sources,
    processes each entry, and logs the execution time.
    """
    start_time = time.time()

    for rss_source in rss_sources:
        rss_source_id, rss_source_link = rss_source
        rss_feed = feedparser.parse(rss_source_link)

        if "status" not in rss_feed:
            error_logger.error(f"Error reading RSS: {rss_source_link}")
            continue

        if rss_feed["status"] != 200:
            error_logger.error(
                f'Error reading RSS: {rss_source_link}, status: {rss_feed["status"]}'
            )
            continue

        for item in rss_feed["entries"]:
            process_feed_item(item, rss_source_id)

    end_time = time.time()
    info_logger.info(f"Script run completed in: {end_time - start_time} seconds")


run_job()
