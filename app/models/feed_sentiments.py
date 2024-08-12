from datetime import datetime

from sqlalchemy import case, func
from sqlalchemy.ext.hybrid import hybrid_property

from libs.database import db


class FeedSentiments(db.Model):
    __tablename__ = "feed_sentiments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feed_id = db.Column(db.Integer, db.ForeignKey("feeds.id"), nullable=False)
    model_id = db.Column(db.Integer)
    prediction = db.Column(db.Text)
    negative = db.Column(db.Float, nullable=False)
    positive = db.Column(db.Float, nullable=False)
    neutral = db.Column(db.Float, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.now, nullable=True)
    created = db.Column(db.DateTime, default=datetime.now)

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
