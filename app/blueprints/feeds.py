from flask import Blueprint, request, render_template
from flask_sqlalchemy.pagination import Pagination

from app.database import get_session, db
from app.models.feeds import Feeds, FeedDBFilters
from config import SOURCES

feeds_bp = Blueprint('feeds', __name__, url_prefix="/feeds")


def get_data(filters: FeedDBFilters = None, page: int = 1, max_per_page: int = 20) -> Pagination:
    session = get_session()

    query = (
        session.query(Feeds)
        .filter(filters.conditions)
        .order_by(Feeds.published.desc())
    )

    print(filters.conditions)

    return db.paginate(query, page=page, max_per_page=max_per_page)



@feeds_bp.route('/')
def index():
    page_title = 'Feeds'
    filters = FeedDBFilters()
    per_page = 30

    filters.process_args(args=request.args)

    page = int(request.args.get('page')) if request.args.get('page') else 1
    if request.args.get('per_page'):
        per_page = int(request.args.get('per_page'))

    feeds = get_data(filters=filters, page=page, max_per_page=per_page)

    filters.sources = ','.join(filters.sources)

    return render_template("pages/feeds.html",
                           page_title=page_title,
                           feeds=feeds,
                           filters=filters.conditions_dict,
                           sources=SOURCES,
                           selected_words=filters.selected_words,
                           page=page,
                           per_page=per_page
                           )
