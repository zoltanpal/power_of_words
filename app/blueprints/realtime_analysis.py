from typing import List

from feedparser import parse as rss_feed_parser
from flask import Blueprint, render_template, request, session
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()

rt_analysis_bp = Blueprint(
    "realtime_analysis", __name__, url_prefix="/realtime_analysis"
)


def process_feed_item(item) -> dict:
    if item["title"]:
        return sid.polarity_scores(item["title"])
    return {}


def get_sentiment_analysis(rss_sources: List[str]):
    sentiment_items: List[dict] = []
    for rss_source_link in rss_sources:
        rss_feed = rss_feed_parser(rss_source_link)

        # Error handling for RSS feed fetching
        if "status" not in rss_feed:
            continue

        if rss_feed["status"] != 200:
            continue

        for item in rss_feed["entries"]:
            if "published" in item:
                published = item["published"]
            elif "lastBuildDate" in item:
                published = item["lastBuildDate"]
            else:
                published = ""
            sentiment_result = process_feed_item(item)
            max_key = max(sentiment_result, key=sentiment_result.get)
            max_value = max(sentiment_result.values())

            sentiment_items.append(
                {
                    "title": item["title"],
                    "published": published,
                    "sentiments": sentiment_result,
                    "is_positive": (
                        "true" if sentiment_result["compound"] > 0.0 else "false"
                    ),
                    "max_sentiment_value": max_value,
                    "max_sentiment_name": max_key,
                    "source": rss_source_link,
                }
            )
    return sentiment_items


@rt_analysis_bp.route("/")
def index():
    page_title = "Real-Time Analysis"
    rss_sentiment_result: List[dict] = []
    session["rss_links"]: List[str] = []

    if request.args.get("rss_links"):
        rss_links = request.args.get("rss_links").split(",")
        session["rss_links"] = rss_links

    if session["rss_links"]:
        rss_sentiment_result = get_sentiment_analysis(session["rss_links"])

    return render_template(
        "pages/realtime_analysis.html",
        page_title=page_title,
        form_rss_links=",".join(session["rss_links"]),
        rss_sentiment_result=rss_sentiment_result,
    )
