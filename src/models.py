from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    activity_id: Optional[int] = Field(default=None, foreign_key="activity.id")


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: int = 0

    participants: List[Participant] = Relationship(back_populates="activity")


# back-populate attribute on Participant (SQLModel requires explicit attribute name)
Participant.activity = Relationship(back_populates="participants")
