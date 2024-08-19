import concurrent.futures
import hashlib
import json
import time

from dateutil import parser as dateparser
from feedparser import parse as rss_feed_parser
from nltk import word_tokenize
from nltk.corpus import stopwords

from config import POW_DB_CONFIG
from libs.functions import clean_url, remove_photo_video, setup_logging_to_file
from libs.pool_db.session import PoolDBSession
from libs.sentiment_analyzer import get_emotion_prediction, get_sentiment_prediction

# Load Hungarian stopwords
stopwords_list = stopwords.words("hungarian")

# Set up logging
error_logger = setup_logging_to_file("jobs/daily/error.log")
info_logger = setup_logging_to_file("jobs/daily/info.log")


def get_rss_sources():
    """Fetches the list of RSS sources from the database."""
    with PoolDBSession(db_config=POW_DB_CONFIG) as session:
        result = session.get_all("sources")
    return result


def not_in_db(hash: str, source_id: int) -> bool:
    """
    Checks if a feed with a given hash and source_id already exists in the database.

    Args:
        hash (str): The MD5 hash of the feed link.
        source_id (int): The ID of the RSS source.

    Returns:
        bool: True if the feed does not exist, False otherwise.
    """

    with PoolDBSession(db_config=POW_DB_CONFIG) as session:
        conditions = {"hash": hash, "source_id": source_id}
        result = session.get_one_where(table="feeds", conditions=conditions)
    return result == 0 or result is None


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

        new_feed = {
            "title": title,
            "link": link,
            "source_id": rss_source_id,
            "words": words,
            "published": published_date,
            "feed_date": feed_date,
            "hash": hash,
            "sentiment_prediction": json.dumps(sentiment_prediction_dict),
            "negative": sentiment_prediction_dict["negative"],
            "positive": sentiment_prediction_dict["positive"],
            "neutral": sentiment_prediction_dict["neutral"],
            "emotion_prediction": json.dumps(emotion_prediction_dict),
            "anger": emotion_prediction_dict["anger"],
            "fear": emotion_prediction_dict["fear"],
            "joy": emotion_prediction_dict["joy"],
            "sadness": emotion_prediction_dict["sadness"],
            "love": emotion_prediction_dict["love"],
            "surprise": emotion_prediction_dict["surprise"],
        }

        with PoolDBSession(db_config=POW_DB_CONFIG) as session:
            session.insert("feeds", **new_feed)


def run_job(rss_source):
    """
    Runs the RSS feed processing job. Fetches RSS feeds from sources,
    processes each entry, and logs the execution time.
    """

    rss_source_id, rss_source_link = rss_source["id"], rss_source["rss"]
    rss_feed = rss_feed_parser(rss_source_link)

    # Error handling for RSS feed fetching
    if "status" not in rss_feed:
        error_logger.error(f"Error reading RSS: {rss_source_link}")
        return

    if rss_feed["status"] != 200:
        error_logger.error(
            f'Error reading RSS: {rss_source_link}, status: {rss_feed["status"]}'
        )
        return

    # Process each item in the feed
    for item in rss_feed["entries"]:
        process_feed_item(item, int(rss_source_id))


def parallel_processing(sources, max_workers=4):
    """Executes RSS processing in parallel using thread pool."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map the run_job function to the list of sources for concurrent execution
        executor.map(run_job, sources)


if __name__ == "__main__":
    start_time = time.time()

    # Fetch the RSS sources from the database
    rss_sources = get_rss_sources()

    # Start parallel processing with a defined number of workers
    parallel_processing(sources=rss_sources, max_workers=len(rss_sources))

    end_time = time.time()
    info_logger.info(f"Script run completed in: {end_time - start_time} seconds")
