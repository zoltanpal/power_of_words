from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Initialize base class for ORM mapping
Base = automap_base()


def initialize_database(app):
    """
    Initializes the database by binding SQLAlchemy to the provided Flask app and
    reflecting the existing database tables.

    Args:
        app (Flask): The Flask application instance.
    """
    # Bind SQLAlchemy to the provided Flask app
    db.init_app(app)

    # Reflect database tables within the application context
    with app.app_context():
        db.reflect()  # Reflect existing database into SQLAlchemy
        Base.prepare(db.engine, reflect=True)  # Prepare the ORM base class


def get_db_session() -> Session:
    """
    Creates and returns a new SQLAlchemy session.

    Returns:
        Session: A new SQLAlchemy session bound to the engine.
    """
    # Create a sessionmaker bound to the SQLAlchemy engine
    session_factory = sessionmaker(bind=db.engine)

    # Return a new session
    try:
        return session_factory()
    finally:
        # Ensure all sessions created by this sessionmaker are closed
        session_factory.close_all()


@contextmanager
def session_scope() -> Session:
    """
    Provides a transactional scope around a series of operations using SQLAlchemy.

    This context manager ensures that a session is properly committed or rolled back,
    and then closed after the operations are complete.

    Yields:
        Session: The SQLAlchemy session to be used within the context.
    """
    # Create a new session using the sessionmaker
    session = sessionmaker(bind=db.engine)()
    try:
        yield session  # Provide the session to the context block
        session.commit()  # Commit the transaction if no exceptions occur
    except Exception:
        session.rollback()  # Roll back the transaction in case of an exception
        raise  # Re-raise the exception to be handled by the caller
    finally:
        session.close()  # Close the session after the operations are complete
