"""
SQLite Database for Dotti Pixel Editor
"""
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./dotti_images.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    pixels = Column(Text, nullable=False)  # JSON: [[r,g,b], ...] 64 entries
    created_at = Column(DateTime, default=datetime.utcnow)

    def get_pixels(self) -> list:
        """Return pixels as list of [r,g,b] tuples."""
        return json.loads(self.pixels)

    def set_pixels(self, pixels: list):
        """Set pixels from list of [r,g,b] tuples."""
        self.pixels = json.dumps(pixels)

    def get_matrix(self) -> list:
        """Return pixels as 8x8 matrix."""
        flat = self.get_pixels()
        return [flat[i*8:(i+1)*8] for i in range(8)]


def init_db():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
