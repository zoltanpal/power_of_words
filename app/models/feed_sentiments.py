from datetime import datetime

from sqlalchemy import func, case
from sqlalchemy.ext.hybrid import hybrid_property

from app.database import db


class FeedSentiments(db.Model):
    __tablename__ = 'feed_sentiments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feeds.id'), nullable=False)
    model_id = db.Column(db.Integer)
    prediction = db.Column(db.Text)
    negative = db.Column(db.Float, nullable=False)
    positive = db.Column(db.Float, nullable=False)
    neutral = db.Column(db.Float, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.now, nullable=True)
    created = db.Column(db.DateTime, default=datetime.now)

    @hybrid_property
    def max_sentiment_value(self):
        return max(self.negative, self.positive, self.neutral)

    @hybrid_property
    def max_sentiment_name(self):
        if self.max_sentiment_value == self.negative:
            return 'negative'
        elif self.max_sentiment_value == self.positive:
            return 'positive'
        else:
            return 'neutral'

    @max_sentiment_value.expression
    def max_sentiment_value(cls):
        return func.GREATEST(cls.negative, cls.positive, cls.neutral)

    @max_sentiment_name.expression
    def max_sentiment_name(cls):
        return case(
            (func.GREATEST(cls.negative, cls.positive, cls.neutral) == cls.negative, 'negative'),
            (func.GREATEST(cls.negative, cls.positive, cls.neutral) == cls.positive, 'positive'),
            else_='neutral'
        )
