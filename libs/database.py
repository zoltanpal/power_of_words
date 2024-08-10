from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from contextlib import contextmanager

engine = None
Base = automap_base()


def initialize_database(db_url):
    global engine
    # Create the engine
    engine = create_engine(db_url)

    # Reflect database tables
    Base.prepare(engine, reflect=True)


def get_session():
    # Create a sessionmaker bound to the SQLAlchemy engine
    Session = sessionmaker(bind=engine)

    # Return a new session
    try:
        return Session()
    finally:
        # Close all sessions created by this sessionmaker
        Session.close_all()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = sessionmaker(bind=engine)()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()