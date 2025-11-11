from sqlmodel import create_engine, SQLModel
from pathlib import Path


DB_FILE = Path(__file__).parent.parent / "activities.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"


def get_engine():
    return create_engine(DATABASE_URL, echo=False)


def init_db():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
