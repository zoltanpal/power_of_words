import json

from config import pow_db_config_str
from libs.database import initialize_database, session_scope
from app.models.feeds import Feeds
from app.models.feed_sentiments import FeedSentiments

initialize_database(pow_db_config_str)

with session_scope() as session:
    feeds = session.query(Feeds.id, Feeds.sentiment_prediction, Feeds.negative, Feeds.positive, Feeds.neutral).all()

    for feed in feeds:
        new_obj = FeedSentiments(
            feed_id=feed[0],
            model_id=1,
            prediction=json.dumps(feed[1]),
            negative=feed[2],
            positive=feed[3],
            neutral=feed[4]
        )
        session.add(new_obj)
        try:
            session.commit()
            print(f"New feed inserted successfully. {feed[0]}")
        except Exception as e:
            session.rollback()  # Rollback the session in case of an error
            print(f"Error occurred: {e}")
        finally:
            session.close()  # Close the session