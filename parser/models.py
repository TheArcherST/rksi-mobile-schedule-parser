from enum import Enum

from datetime import date, datetime, time

from dataclasses import dataclass

from pydantic import BaseModel, Field
from beanie import Document


class ThemeSource:
    pass


class SourcesReference(BaseModel):
    """SourcesReference model

    Contains accepted contacts

    """

    data: str


class SubjectEntry(BaseModel):
    """SubjectEntry model

    SubjectEntry

    """

    startsAt: datetime
    endsAt: datetime
    name: str

    removedAt: datetime


class Group(Document):
    name: str
    schedule: list[SubjectEntry]
    lastUpdate: datetime = Field(default_factory=datetime.now)
    removedAt: datetime = None


@dataclass
class RawSubjectEntry:
    starts_at: time = None
    ends_at: time = None
    teacher: str = None
    audience: str = None
    name: str = None
    date: date = None
