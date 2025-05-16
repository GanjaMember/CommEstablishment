from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.infrastructure.database.models import Base


class DatabaseManager:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.SessionFactory = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables defined in the models."""
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Drop all tables defined in the models."""
        Base.metadata.drop_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionFactory()
