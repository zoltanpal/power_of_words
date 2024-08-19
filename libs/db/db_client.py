from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker


class SQLDBClient:
    def __init__(
        self, db_config, auto_commit=False, expire_on_commit=False, auto_flush=False
    ):
        if db_config is None:
            raise ValueError("Missing database configuration.")

        self.auto_commit = auto_commit
        self.auto_flush = auto_flush
        self.expire_on_commit = expire_on_commit

        self.connection_string = (
            f"{db_config.dialect}://{db_config.username}:{db_config.password}@"
            f"{db_config.host}:{db_config.port}/{db_config.dbname}"
        )
        self.engine = self.create_engine()
        self.session_local = self.create_session()

    def create_engine(self):
        """SQLAlchemy database connection engine factory"""
        try:
            return create_engine(self.connection_string, pool_pre_ping=True)
        except SQLAlchemyError as ex:
            error = str(ex.__dict__["orig"])
            raise SQLAlchemyError(error) from ex

    def create_session(self):
        """SQLAlchemy database session factory"""
        return sessionmaker(
            autocommit=self.auto_commit,
            autoflush=self.auto_flush,
            expire_on_commit=self.expire_on_commit,
            bind=self.engine,
        )

    @contextmanager
    def get_db_session(
        self, auto_commit=False, auto_flush=False, expire_on_commit=False
    ) -> Session:
        """Create SQLAlchemy database session"""
        session = self.session_local()
        session.autocommit = auto_commit
        session.autoflush = auto_flush
        session.expire_on_commit = expire_on_commit

        try:
            yield session
        finally:
            session.close()
            self.engine.dispose()

    def get_session(self) -> Session:
        """Create SQLAlchemy DB session"""
        if self.session_local is None:
            return None
        session = self.session_local()
        try:
            yield session
        finally:
            session.close()
            self.engine.dispose()
