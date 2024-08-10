from dataclasses import dataclass, field, fields
from datetime import datetime, timedelta
from typing import List

from flask import request
from sqlalchemy import and_, text, func, case
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import to_tsquery
from sqlalchemy.ext.hybrid import hybrid_property

from app.database import db


class Feeds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    link = db.Column(db.String)
    hash = db.Column(db.String)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
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



@dataclass
class FeedDBFilters:
    one_week_ago = datetime.now() - timedelta(days=7)

    words: List[str] = field(default_factory=list)
    sources: List[int] = field(default_factory=list)
    start_date: str = field(default=(one_week_ago.strftime("%Y-%m-%d 00:00:00")))
    end_date: str = field(default=(datetime.now().strftime("%Y-%m-%d 23:59:59")))
    free_text: str = field(default='')
    selected_words: List[str] = field(default_factory=list)

    def generate_conditions(self):
        conditions = []

        if self.start_date:
            conditions.append(Feeds.feed_date >= self.start_date)

        if self.end_date:
            conditions.append(Feeds.feed_date <= self.end_date)

        if self.words:
            words_cond = [word.lower().strip() for word in self.words]
            conditions.append(Feeds.words.contains(words_cond))

        if self.sources:
            sources_cond = [int(source) for source in self.sources]
            conditions.append(Feeds.source_id.in_(sources_cond))

        if self.free_text:
            #free_text_array = self.free_text.split(',')
            #tsquery_parts = " & ".join([f"to_tsquery('simple', :term{i})" for i in range(len(free_text_array))])
            #tsquery_expr = f"search_vector @@ {tsquery_parts}"
            #conditions.append(Feeds.search_vector.op('@@')(to_tsquery(self.free_text)))
            search = f"%{self.free_text}%"
            conditions.append(Feeds.title.ilike(search))

        # Create and_ clause if there are conditions
        return and_(*conditions) if conditions else None

    '''
    def generate_query_conditions(self):
        conditions = []

        if self.start_date:
            conditions.append(f'feed_date >= {self.start_date}')

        if self.end_date:
            conditions.append(f'feed_date <= {self.end_date}')

        if self.words:
            words_cond = [word.lower().strip() for word in self.words]
            conditions.append(Feeds.words.contains(words_cond))

        if self.sources:
            sources_cond = [int(source) for source in self.sources]
            conditions.append(Feeds.source_id.in_(sources_cond))

        if self.free_text:
            search = f"%{self.free_text}%"
            conditions.append(Feeds.title.ilike(search))

    @property
    def query_conditions(self):
        return self.generate_query_conditions()
    '''

    @property
    def conditions(self):
        return self.generate_conditions()

    @property
    def conditions_dict(self):
        params_dict = {}
        for field in fields(self):
            if field_value := getattr(self, field.name):
                params_dict[field.name] = field_value

        return params_dict

    def process_args(self, args: dict):
        if args.get('start_date') != '' and args.get('start_date') is not None:
            self.start_date = args.get('start_date')

        if args.get('end_date') != '' and args.get('end_date') is not None:
            self.end_date = args.get('end_date')

        if args.get('sources'):
            # self.sources = [int(s) for s in args.get('sources').split(',')]
            self.sources = args.get('sources').split(',')

        if args.get('words'):
            self.words = args.get('words').split(',')
            self.selected_words.extend(self.words)

        if request.args.get('free_text'):
            self.free_text = args.get('free_text')
            self.selected_words.append(self.free_text)
