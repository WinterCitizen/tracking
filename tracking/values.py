from datetime import datetime, timedelta

from pydantic import BaseModel


class WorklogValue(BaseModel):
    issue: str
    started_at: datetime
    spent: timedelta
    comment: str

    class Config:
        frozen = True


class SavedWorklogValue(BaseModel):
    id: str
    created_at: datetime
    worklog: WorklogValue

    class Config:
        frozen = True
