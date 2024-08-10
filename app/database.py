from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker

db = SQLAlchemy()
Base = automap_base()


def initialize_database(app):
    # Bind SQLAlchemy to the provided Flask app
    db.init_app(app)

    # Reflect database tables within the application context
    with app.app_context():
        db.reflect()
        Base.prepare(db.engine, reflect=True)


def get_session():
    # Create a sessionmaker bound to the SQLAlchemy engine
    Session = sessionmaker(bind=db.engine)

    # Return a new session
    try:
        return Session()
    finally:
        # Close all sessions created by this sessionmaker
        Session.close_all()



@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = sessionmaker(bind=db.engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
