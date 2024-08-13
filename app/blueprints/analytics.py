from collections import Counter
from typing import List

from flask import Blueprint, render_template, request
from sqlalchemy import text

from app.models.feed_db_filters import FeedDBFilters
from app.models.feeds import Feeds
from config import SOURCES
from libs.database import get_session

analytics_bp = Blueprint("charts", __name__, url_prefix="/analytics")

SOURCES_NAME_LIST = list(SOURCES.values())
IGNORED_WORDS = ["magyar", "egy", "két", "miatt", "ezért"]


def get_sentiment_grouped(
    filters: FeedDBFilters, group_by: str = "source_id", order_by: str = "source_id ASC"
):
    words_in = f" AND (words @> ARRAY{filters.words})" if filters.words else ""
    text_like = (
        f" AND lower(title) LIKE lower('%{filters.free_text}%')"
        if filters.free_text
        else ""
    )
    stmt = f"""
            SELECT {group_by}, count(id) as count,
            CASE
                WHEN GREATEST(negative, positive, neutral) = negative THEN 'negative'
                WHEN GREATEST(negative, positive, neutral) = positive THEN 'positive'
                ELSE 'neutral'
            END AS max_sentiment_column
            -- GREATEST(negative, positive, neutral) AS max_sentiment_value
        FROM feeds
        WHERE published >= :start_date and published <= :end_date {text_like}{words_in}
        GROUP BY {group_by}, max_sentiment_column
        ORDER BY {order_by};
    """

    session = get_session()

    return session.execute(
        text(stmt),
        {"start_date": filters.start_date, "end_date": filters.end_date},
    ).all()


def generate_sentiment_by_source_series(input_data):
    negative_data = {}
    neutral_data = {}
    positive_data = {}

    for item in input_data:
        key = item[0]  # position
        value = item[1]  # data
        sentiment = item[2]

        if sentiment == "negative":
            if key not in negative_data:
                negative_data[key] = []
            negative_data[key].append(value)
        elif sentiment == "neutral":
            if key not in neutral_data:
                neutral_data[key] = []
            neutral_data[key].append(value)
        elif sentiment == "positive":
            if key not in positive_data:
                positive_data[key] = []
            positive_data[key].append(value)

    series_data = {"Negative": [], "Neutral": [], "Positive": []}
    for key in sorted(
        set(negative_data.keys()) | set(neutral_data.keys()) | set(positive_data.keys())
    ):
        series_data["Negative"].extend(negative_data.get(key, [0]))
        series_data["Neutral"].extend(neutral_data.get(key, [0]))
        series_data["Positive"].extend(positive_data.get(key, [0]))

    return series_data


def get_most_common_words(filters, most_common: int = 20):
    session = get_session()

    cursor_result = session.query(
        Feeds.words,
    ).filter(filters.conditions)

    """
    words = []
    for row_words in list(cursor_result):
        [words.append(word) for word in row_words[0] if word not in IGNORED_WORDS] # numpy complains about this
    """

    words: List[str] = []
    for row_words in list(cursor_result):
        words.extend(word for word in row_words[0] if word not in IGNORED_WORDS)

    return Counter(words).most_common(most_common)


@analytics_bp.route("/")
def index():
    page_title = "Analytics"
    filters = FeedDBFilters()

    filters.process_args(args=request.args)

    sentiment_by_source = get_sentiment_grouped(filters)
    sentiment_by_source_series = generate_sentiment_by_source_series(
        sentiment_by_source
    )

    sentiment_by_time = get_sentiment_grouped(
        filters=filters, group_by="feed_date", order_by="feed_date"
    )
    sentiment_by_time_series = generate_sentiment_by_source_series(sentiment_by_time)

    sentiment_by_time_series_dates = {
        row[0].strftime("%Y-%m-%d") for row in sentiment_by_time
    }

    most_common_words_raw = get_most_common_words(filters=filters, most_common=40)
    most_common_words: List[dict] = [
        {"name": word[0], "weight": word[1]} for word in most_common_words_raw
    ]  # pragme: no cover
    return render_template(
        "pages/analytics.html",
        page_title=page_title,
        categories=SOURCES_NAME_LIST,
        filters=filters,
        most_common_words=most_common_words,
        sentiment_by_source_series=sentiment_by_source_series,
        sentiment_by_time_series=sentiment_by_time_series,
        sentiment_by_time_series_dates=sorted(list(sentiment_by_time_series_dates)),
    )
