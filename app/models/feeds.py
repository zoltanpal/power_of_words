from datetime import datetime

from sqlalchemy import case, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property

from libs.database import db


class Feeds(db.Model):
    """Represents a feed entry in the database."""

    __tablename__ = "feeds"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    link = db.Column(db.String)
    hash = db.Column(db.String)
    source_id = db.Column(db.Integer, db.ForeignKey("sources.id"))
    words = db.Column(postgresql.ARRAY(db.Text), default=[])
    published = db.Column(db.DateTime)
    feed_date = db.Column(db.Date)
    sentiment_prediction = db.Column(db.Text)
    negative = db.Column(db.Float)
    positive = db.Column(db.Float)
    neutral = db.Column(db.Float)
    emotion_prediction = db.Column(db.Text)
    anger = db.Column(db.Float)
    fear = db.Column(db.Float)
    joy = db.Column(db.Float)
    sadness = db.Column(db.Float)
    love = db.Column(db.Float)
    surprise = db.Column(db.Float)
    updated = db.Column(db.DateTime, default=datetime.now)
    created = db.Column(db.DateTime, default=datetime.now)
    search_vector = db.Column()

    @hybrid_property
    def max_sentiment_value(self) -> float:
        """
        Returns the maximum sentiment score among negative, positive, and neutral.

        Returns:
            float: The highest sentiment score.
        """
        return max(self.negative, self.positive, self.neutral)

    @max_sentiment_value.expression
    def max_sentiment_value_expr(cls):
        """
        SQL expression for calculating the maximum sentiment score in the database query.

        Returns:
            sqlalchemy.sql.expression: The SQL expression for the greatest sentiment score.
        """
        return func.GREATEST(cls.negative, cls.positive, cls.neutral)

    @hybrid_property
    def max_sentiment_name(self) -> str:
        """
        Returns the name of the sentiment with the highest score.

        Returns:
            str: "negative", "positive", or "neutral" based on the highest sentiment score.
        """
        if self.max_sentiment_value == self.negative:
            return "negative"
        elif self.max_sentiment_value == self.positive:
            return "positive"
        else:
            return "neutral"

    @max_sentiment_name.expression
    def max_sentiment_name_expr(cls):
        """
        SQL expression for determining the name of the sentiment with the highest score in a database query.

        Returns:
            sqlalchemy.sql.expression: The SQL expression for the sentiment name with the greatest score.
        """
        return case(
            (
                func.GREATEST(cls.negative, cls.positive, cls.neutral) == cls.negative,
                "negative",
            ),
            (
                func.GREATEST(cls.negative, cls.positive, cls.neutral) == cls.positive,
                "positive",
            ),
            else_="neutral",
        )
