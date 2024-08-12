from datetime import datetime

from sqlalchemy import text, update

from config import pow_db_config
from libs.db.db_client import SQLDBClient
from libs.db.db_mapping import SQLDBMapping
from libs.functions import remove_photo_video

db_client = SQLDBClient(db_config=pow_db_config)

TITLES_WITH_FOTO_VIDEO = """
select id, title, words, source_id from feeds where title like '%- videó%' or title like '%- fotó%';
"""

db_mapping = SQLDBMapping(db_client=db_client)
Feeds = db_mapping.db_classes.feeds


def remove_numbers_from_words():
    pass


def remove_foto_video_text():
    with db_client.get_db_session() as session:
        result = session.execute(text(TITLES_WITH_FOTO_VIDEO)).fetchall()
    updated_ids = []
    words_pattern = ["videó", "videók", "fotó", "fotók", "videókkal", "fotókkal"]
    if result:
        rows = list(result)
        for row in rows:
            feed_id = row[0]
            cleaned_title = remove_photo_video(row[1]).strip()
            cleaned_words = [item for item in row[2] if item not in words_pattern]

            stmt = (
                update(Feeds)
                .where(Feeds.id == feed_id)
                .values(
                    title=cleaned_title, words=cleaned_words, updated=datetime.now()
                )
            )

            session.execute(stmt)
            session.commit()
            updated_ids.append(feed_id)

    return updated_ids


res = remove_foto_video_text()
print(res)
